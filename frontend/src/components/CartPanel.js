// components/CartPanel.js
import React from "react";
import Image from "next/image";

export default function CartPanel({ cart, onClose }) {
  const total = cart
    .reduce((sum, item) => sum + item.price * item.quantity, 0)
    .toFixed(2);

  return (
    <div className="fixed right-0 top-0 w-1/3 h-full bg-white text-gray-900 p-6 shadow-lg overflow-y-auto transition duration-300 ease-in-out">
      <button onClick={onClose} className="absolute top-4 right-4 text-white">
        X
      </button>
      <h2 className="text-xl font-semibold mb-4">My Cart</h2>
      <div className="space-y-4">
        {cart.map((item) => (
          <div key={item.product_id} className="flex justify-between items-end">
            <Image
              src={item.thumbnail}
              alt={item.title}
              width={64}
              height={64}
              className="object-cover rounded"
            />
            <div className="ml-4 flex-1">
              <h3 className="text-lg">{item.title}</h3>
              <p className="text-gray-400">
                ${item.price.toFixed(2)} x {item.quantity}
              </p>
            </div>
            <div>${(item.price * item.quantity).toFixed(2)}</div>
          </div>
        ))}
      </div>
      <hr className="my-4" />
      <div className="flex justify-between text-lg font-semibold">
        <p>Total</p>
        <p>${total} USD</p>
      </div>
      <button className="mt-6 bg-blue-600 w-full py-2 rounded text-gray-900 font-bold">
        Proceed to Checkout
      </button>
    </div>
  );
}
