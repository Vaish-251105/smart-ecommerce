import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { wishlistAPI } from '../utils/api';
import { useCart } from '../context/CartContext';
import { formatINR } from '../utils/currency';
import toast from 'react-hot-toast';
import PremiumImage from '../components/PremiumImage';
import { FiTrash2, FiShoppingCart, FiHeart, FiArrowLeft } from 'react-icons/fi';

const WishlistPage = () => {
    const [wishlist, setWishlist] = useState([]);
    const [loading, setLoading] = useState(true);
    const { addToCart } = useCart();

    useEffect(() => { fetchWishlist(); }, []);

    const fetchWishlist = async () => {
        try {
            const { data } = await wishlistAPI.get();
            setWishlist(data.wishlist?.products || []);
        } catch (error) {
            console.error('Wishlist fetch error:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleRemove = async (productId) => {
        try {
            await wishlistAPI.remove(productId);
            setWishlist(prev => prev.filter(p => p._id !== productId));
            toast.success('Removed from wishlist');
        } catch (error) {
            toast.error('Failed to remove');
        }
    };

    const handleAddToCart = async (product) => {
        try {
            await addToCart(product._id);
            toast.success(`${product.name} added to cart!`);
        } catch (error) {
            toast.error(error.response?.data?.error || 'Failed to add to cart');
        }
    };

    if (loading) return <div className="main-content"><div className="loading-spinner"><div className="spinner" /></div></div>;

    return (
        <div className="main-content">
            <div className="container" style={{ padding: '40px 24px' }}>
                <div className="page-header">
                    <h1 className="page-title"><FiHeart style={{ color: '#ef4444' }} /> My Wishlist</h1>
                    <p className="page-subtitle">{wishlist.length} item{wishlist.length !== 1 ? 's' : ''} saved</p>
                </div>

                {wishlist.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-state-icon">💝</div>
                        <h3>Your wishlist is empty</h3>
                        <p>Save your favorite products to buy later!</p>
                        <Link to="/products" className="btn btn-primary">Browse Products</Link>
                    </div>
                ) : (
                    <div className="products-grid">
                        {wishlist.map((product) => (
                            <div key={product._id} className="product-card" style={{ position: 'relative' }}>
                                <button
                                    onClick={(e) => { e.stopPropagation(); handleRemove(product._id); }}
                                    style={{
                                        position: 'absolute', top: '12px', right: '12px', zIndex: 5,
                                        background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)',
                                        borderRadius: '50%', width: '36px', height: '36px',
                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        cursor: 'pointer', color: '#ef4444', transition: 'all 0.2s'
                                    }}
                                    title="Remove from wishlist"
                                >
                                    <FiTrash2 size={15} />
                                </button>

                                <Link to={`/products/${product._id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                                    <div className="product-card-image">
                                        <PremiumImage src={product.imageURL} alt={product.name} />
                                    </div>
                                    <div className="product-card-body">
                                        <div className="product-card-category">{product.category}</div>
                                        <h3 className="product-card-name">{product.name}</h3>
                                        <div className="product-card-footer">
                                            <div className="product-price">
                                                <span style={{ color: '#0f1111', fontWeight: 700 }}>{formatINR(product.price)}</span>
                                                {product.basePrice > product.price && (
                                                    <span className="original-price">{formatINR(product.basePrice)}</span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </Link>

                                <div style={{ padding: '0 16px 16px' }}>
                                    <button
                                        className="btn btn-primary btn-full btn-sm"
                                        onClick={() => handleAddToCart(product)}
                                        disabled={product.stockQuantity === 0}
                                    >
                                        <FiShoppingCart size={14} />
                                        {product.stockQuantity === 0 ? 'Out of Stock' : 'Add to Cart'}
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default WishlistPage;
