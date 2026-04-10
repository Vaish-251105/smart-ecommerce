from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from store.models import Product
from orders.models import Order, OrderItem
from django.conf import settings
from django.db.models import Q
import openai

# --- Existing Recommendation Logic ---
@api_view(['GET'])
def recommend_products(request, user_id):
    orders = OrderItem.objects.filter(order__user_id=user_id)
    product_ids = orders.values_list('product_id', flat=True)
    recommended = Product.objects.exclude(id__in=product_ids)[:5]
    
    data = [{"id": p.id, "name": p.name, "price": p.price} for p in recommended]
    return Response({"recommended_products": data})

# --- New AI Chatbot Logic ---
class ChatbotAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_query = request.data.get("query", "").lower()
        if not user_query:
            return Response({"error": "Query is required"}, status=400)

        # --- 1. SMART RETRIEVAL (RAG) ---
        # Search products based on keywords in query
        keywords = user_query.split()
        
        # Build Q object for multi-keyword search
        query_filter = Q()
        for kw in keywords:
            if len(kw) > 3: # Ignore small words
                query_filter |= Q(name__icontains=kw) | Q(description__icontains=kw) | Q(category__name__icontains=kw)
        
        matched_products = Product.objects.filter(query_filter).distinct()[:10]
        
        # If no specific matches, get Featured products
        if not matched_products.exists():
            matched_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]

        product_context = "\n".join([
            f"- {p.name} [ID:{p.id}]: ₹{p.price} | Cat: {p.category.name if p.category else 'General'} | Specs: {p.description[:100]}..."
            for p in matched_products
        ])

        # --- 2. LOGIC FOR COMPARISONS ---
        # If user asks to compare, we provide more detailed specs
        comparison_context = ""
        if "compare" in user_query:
            comparison_context = "Detailed Comparison Data:\n"
            for p in matched_products[:3]: # Compare up to 3
                comparison_context += f"Product: {p.name}\nPrice: ₹{p.price}\nFeatures: {p.description}\n\n"

        # --- 3. RECENT ORDERS CONTEXT ---
        user_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:2]
        order_list = [f"Order #{o.id} ({o.status})" for o in user_orders]
        order_context = f"User's Status: {', '.join(order_list) if order_list else 'No recent orders'}"

        system_prompt = f"""
        You are 'BloomBot', a high-end AI shopping assistant for 'Bloom & Buy'.
        You have access to real-time inventory and user order data.
        
        RELEVANT PRODUCTS FOR THIS QUERY:
        {product_context}
        
        {comparison_context}
        
        USER INFO:
        {order_context}
        
        CORE CAPABILITIES:
        1. Recommendations: Suggest products from the list above based on user's budget and requirements.
        2. Comparison: Use the 'Detailed Comparison Data' if available to provide a side-by-side spec comparison.
        3. Classification: If the user query is vague, suggest categories based on common shopping needs.
        4. Tracking: If asked about an order, reference the Order ID from USER INFO and explain they can track it in 'My Orders'.
        
        STRICT RULES:
        - ONLY recommend products from the provided list.
        - Always use ₹ for currency.
        - If budget is mentioned (e.g., 'under 20000'), prioritize products in that range.
        - If you don't have enough data, ask clarifying questions (e.g., 'What is your budget?').
        """

        try:
            api_key = getattr(settings, 'OPENAI_API_KEY', None)
            if not api_key or api_key.startswith('sk-placeholder'):
                # Intelligent Fallback response even without API key
                best_match = matched_products.first()
                match_text = f"Based on your query, I found {matched_products.count()} items including '{best_match.name}' for ₹{best_match.price}." if best_match else "I'm looking at our catalog now."
                return Response({
                    "response": f"I'm BloomBot! {match_text} (AI is in Demo Mode - configure OpenAI API key for full logic). How can I help further?",
                    "is_mock": True,
                    "matched_count": matched_products.count()
                })

            client = openai.OpenAI(api_key=api_key)
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.7
            )
            ai_response = completion.choices[0].message.content
            return Response({"response": ai_response, "is_mock": False})

        except Exception as e:
            return Response({
                "response": "I'm having trouble connecting to my brain right now, but I can still tell you about our products!",
                "error": str(e)
            }, status=500)