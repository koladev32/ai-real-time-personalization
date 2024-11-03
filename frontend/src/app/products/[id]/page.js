// app/products/[id]/page.js
"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { fetchFromAPI } from "@/utils/api";
import { getSessionId } from "@/utils/session";
import { use } from "react";
import { trackEvent } from "@/utils/tracking";

export default function ProductPage({ params }) {
  const [product, setProduct] = useState(null);
  const [relatedProducts, setRelatedProducts] = useState([]);
  const productId = use(params).id;

  useEffect(() => {
    async function fetchProductDetails() {
      const productData = await fetchFromAPI(`/products/${productId}`);
      setProduct(productData);

      // Fetch related products from the same category
      if (productData && productData.category_id) {
        const related = await fetchFromAPI(
          `/products?category=${productData.category_id}&limit=4`
        );
        setRelatedProducts(related.products);
      }
    }
    fetchProductDetails();
  }, [productId]);

  useEffect(() => {
    if(product) {
      trackEvent("view_product", { product_id: product.id, category_id: product?.category_id });
    }
  }, [product]);

  const handleAddToCart = () => {
    trackEvent("add_to_cart", {
      product_id: product.id,
      price: product.price,
      quantity: 1,
      category_id: product?.category_id
    });
  };

  // Add product to cart
  const addToCart = () => {
    const sessionId = getSessionId();
    const cartItem = {
      product_id: product.id,
      title: product.title,
      price: product.price,
      quantity: 1,
    };

    // Save to localStorage
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
    cart.push(cartItem);
    localStorage.setItem("cart", JSON.stringify(cart));

    // Send to backend
    fetchFromAPI("/cart", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, ...cartItem }),
    });

    handleAddToCart();
  };

  if (!product) return <div>Loading...</div>;

  return (
    <div className="p-6">
      {/* Product Details */}
      <h1 className="text-3xl font-bold">{product.title}</h1>
      <p className="text-xl text-blue-400">${product.price.toFixed(2)}</p>
      <p className="text-gray-500 mt-2">{product.description}</p>
      <p className="text-gray-500">Rating: {product.rating}</p>
      <button
        onClick={addToCart}
        className="bg-blue-600 text-white px-4 py-2 rounded mt-4"
      >
        Add to Cart
      </button>

      {/* Related Products */}
      <h2 className="text-2xl font-bold mt-8">Related Products</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {relatedProducts.map((related) => (
          <div key={related.id} className="bg-gray-800 p-4 rounded-lg">
            <Image
              src={
                related.thumbnail ||
                `https://dummyjson.com/image/400x200/FF0000/FFFFFF?text=${product.title.replace(
                  " ",
                  "+"
                )}`
              }
              alt={related.title}
              width={300}
              height={200}
              className="w-full h-32 object-cover rounded"
            />
            <h3 className="mt-2 text-lg font-semibold">{related.title}</h3>
            <p className="text-blue-400">${related.price.toFixed(2)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
