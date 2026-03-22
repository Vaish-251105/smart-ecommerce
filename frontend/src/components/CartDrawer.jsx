import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { formatINR } from '../utils/currency';
import { FiX, FiTrash2, FiShoppingBag, FiArrowRight } from 'react-icons/fi';
import PremiumImage from './PremiumImage';

const CartDrawer = () => {
    const { 
        cart, subtotal, itemCount, 
        updateQuantity, removeFromCart, 
        isDrawerOpen, closeDrawer 
    } = useCart();
    
    const { isAuthenticated } = useAuth();
    const navigate = useNavigate();
    const [isClosing, setIsClosing] = useState(false);

    // Prevent body scroll when drawer is open
    useEffect(() => {
        if (isDrawerOpen) {
            document.body.style.overflow = 'hidden';
            setIsClosing(false);
        } else {
            document.body.style.overflow = '';
        }
        return () => {
            document.body.style.overflow = '';
        };
    }, [isDrawerOpen]);

    const handleClose = () => {
        setIsClosing(true);
        setTimeout(() => {
            closeDrawer();
            setIsClosing(false);
        }, 300); // match CSS animation duration
    };

    const handleCheckout = () => {
        handleClose();
        navigate('/checkout');
    };

    if (!isDrawerOpen && !isClosing) return null;

    return (
        <>
            <div className="cart-drawer-overlay" onClick={handleClose} />
            <div className={`cart-drawer ${isClosing ? 'closing' : ''}`}>
                <div className="cart-drawer-header">
                    <h2 className="cart-drawer-title">
                        Your Cart <span className="count">{itemCount}</span>
                    </h2>
                    <button className="cart-drawer-close" onClick={handleClose}>
                        <FiX size={20} />
                    </button>
                </div>

                <div className="cart-drawer-body">
                    {!isAuthenticated ? (
                        <div className="empty-drawer">
                            <FiShoppingBag className="empty-drawer-icon" />
                            <h3 style={{ marginBottom: '8px', color: 'var(--text-primary)' }}>Please log in</h3>
                            <p style={{ fontSize: '0.9rem', marginBottom: '24px' }}>Log in to view your cart items.</p>
                            <button 
                                className="btn btn-primary"
                                onClick={() => { handleClose(); navigate('/login'); }}
                            >
                                Login
                            </button>
                        </div>
                    ) : !cart.items || cart.items.length === 0 ? (
                        <div className="empty-drawer">
                            <FiShoppingBag className="empty-drawer-icon" />
                            <h3 style={{ marginBottom: '8px', color: 'var(--text-primary)' }}>Your cart is empty</h3>
                            <p style={{ fontSize: '0.9rem', marginBottom: '24px' }}>Discover our premium collections.</p>
                            <button 
                                className="btn btn-primary"
                                onClick={() => { handleClose(); navigate('/products'); }}
                            >
                                Start Shopping
                            </button>
                        </div>
                    ) : (
                        cart.items.map((item) => {
                            const product = item.product;
                            if (!product) return null;
                            return (
                                <div key={item._id} className="drawer-item">
                                    <div className="drawer-item-img">
                                        <PremiumImage 
                                            src={product.imageURL} 
                                            alt={product.name} 
                                            fallbackIconSize={20} 
                                        />
                                    </div>
                                    <div className="drawer-item-content">
                                        {product.seller?.storeName && (
                                            <div className="drawer-item-brand">{product.seller.storeName}</div>
                                        )}
                                        <div className="drawer-item-name">{product.name}</div>
                                        <div className="drawer-item-price">{formatINR(product.price)}</div>
                                        
                                        <div className="drawer-item-controls">
                                            <div className="drawer-qty-box">
                                                <button 
                                                    className="drawer-qty-btn"
                                                    onClick={() => item.quantity > 1 && updateQuantity(product._id, item.quantity - 1)}
                                                >−</button>
                                                <span className="drawer-qty-val">{item.quantity}</span>
                                                <button 
                                                    className="drawer-qty-btn"
                                                    onClick={() => updateQuantity(product._id, item.quantity + 1)}
                                                >+</button>
                                            </div>
                                            <button 
                                                className="drawer-item-remove"
                                                onClick={() => removeFromCart(product._id)}
                                            >
                                                <FiTrash2 size={14} /> Remove
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            );
                        })
                    )}
                </div>

                {isAuthenticated && cart.items?.length > 0 && (
                    <div className="cart-drawer-footer">
                        <div className="drawer-summary-row">
                            <span>Subtotal</span>
                            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{formatINR(subtotal)}</span>
                        </div>
                        <div className="drawer-summary-row">
                            <span>Shipping</span>
                            <span style={{ color: subtotal > 4150 ? 'var(--success)' : 'inherit' }}>
                                {subtotal > 4150 ? 'Free' : formatINR(50)}
                            </span>
                        </div>
                        <div className="drawer-summary-total">
                            <span>Total</span>
                            <span>{formatINR(subtotal + (subtotal > 4150 ? 0 : 50))}</span>
                        </div>
                        
                        <button 
                            className="btn btn-primary btn-full btn-lg" 
                            style={{ marginTop: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                            onClick={handleCheckout}
                        >
                            <span>Checkout</span>
                            <FiArrowRight />
                        </button>
                    </div>
                )}
            </div>
        </>
    );
};

export default CartDrawer;
