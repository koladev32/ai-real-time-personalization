// components/Navbar.js
"use client";

import { useEffect } from "react";
import CartIcon from "./CartIcon";
import SearchBar from "./SearchBar";
import useCart from "@/hooks/useCart";

export default function Navbar({
  setSearchTerm,
  cartCount,
  isCartOpen,
  setIsCartOpen,
}) {
  return (
    <nav className="flex justify-between bg-white text-gray-900">
      <h1 className="w-1/3 text-xl font-bold">RAD STORE</h1>
      <div className="flex justify-between items-center mb-6 w-3/4">
        <SearchBar onSearch={setSearchTerm} />
      </div>
      <div className="flex">
        <CartIcon
          count={cartCount}
          onClick={() => setIsCartOpen(!isCartOpen)}
        />
      </div>
    </nav>
  );
}
