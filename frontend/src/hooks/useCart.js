// hooks/useCart.js
import { useState, useEffect } from "react";
import { getSessionId } from "../utils/session";
import { fetchFromAPI } from "../utils/api";

export default function useCart() {
  const [cart, setCart] = useState([]);
  const [cartCount, setCartCount] = useState(0);
  const [isCartOpen, setIsCartOpen] = useState(false);

  useEffect(() => {
    const loadCart = async () => {
      const cartData = await fetchFromAPI(`/cart`);
      setCart(cartData.items || []);
      setCartCount(
        cartData.items?.reduce((total, item) => total + item.quantity, 0) || 0
      );
    };

    loadCart();
  }, []);

  const addToCart = async (productId, quantity = 1) => {
    const sessionId = getSessionId();
    const response = await fetchFromAPI("/cart", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        product_id: productId,
        quantity,
      }),
    });

    if (response.status === "success") {
      // Update local cart state
      const updatedCart = [...cart];
      const itemIndex = updatedCart.findIndex(
        (item) => item.product_id === productId
      );
      if (itemIndex !== -1) {
        updatedCart[itemIndex].quantity += quantity;
      } else {
        const productData = await fetchFromAPI(`/products/${productId}`);
        updatedCart.push({ ...productData, quantity });
      }
      setCart(updatedCart);
      setCartCount(
        updatedCart.reduce((total, item) => total + item.quantity, 0)
      );
    }
  };

  return { cart, cartCount, isCartOpen, setIsCartOpen, addToCart };
}
