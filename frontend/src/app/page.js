// app/page.js
"use client";
import { useState, useEffect } from "react";
import ProductCard from "../components/ProductCard";
import SortMenu from "../components/SortMenu";
import Pagination from "../components/Pagination";
import Sidebar from "../components/Sidebar";
import { fetchFromAPI } from "../utils/api";
import Navbar from "../components/Navbar";
import CartPanel from "../components/CartPanel";
import useCart from "../hooks/useCart";

export default function Home() {
  
  const [products, setProducts] = useState([]);
  const [totalProducts, setTotalProducts] = useState(0);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortOption, setSortOption] = useState({
    field: "",
    order: "",
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedCategory, setSelectedCategory] = useState("");
  const productsPerPage = 12;
  const { cart, isCartOpen, setIsCartOpen, cartCount } = useCart();

  useEffect(() => {
    async function fetchProducts() {
      try {
        const params = {
          limit: productsPerPage,
          skip: (currentPage - 1) * productsPerPage,
          sortBy: sortOption.field || "id",
          order: sortOption.order || "asc",
        };
        if (searchTerm) params.search = searchTerm;
        if (selectedCategory) params.category = selectedCategory;

        const data = await fetchFromAPI("/products", { params });
        setProducts(data.products);
        setTotalProducts(data.total);
      } catch (error) {
        console.error("Failed to fetch products:", error);
      }
    }
    fetchProducts();
  }, [searchTerm, sortOption, currentPage, selectedCategory]);

  return (
    <>
      <main className={`flex-1 p-6 ${isCartOpen ? "opacity-25" : ""}`}>
        <div className="flex flex-col">
          <Navbar
            setSearchTerm={setSearchTerm}
            setIsCartOpen={setIsCartOpen}
            cartCount={cartCount}
            isCartOpen={isCartOpen}
          />
          <div className="flex">
            <Sidebar onCategorySelect={setSelectedCategory} />
            <main className="px-6 flex flex-row space-x-4">
              <div className="w-10/12">
                <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-3 gap-6">
                  {products.map((product) => (
                    <ProductCard key={product.id} product={product} />
                  ))}
                </div>
                <Pagination
                  currentPage={currentPage}
                  totalPages={Math.ceil(totalProducts / productsPerPage)}
                  onPageChange={setCurrentPage}
                />
              </div>
              <SortMenu onSort={(option) => setSortOption(option)} />
            </main>
          </div>
        </div>
      </main>
      {isCartOpen && (
        <CartPanel cart={cart} onClose={() => setIsCartOpen(false)} />
      )}
    </>
  );
}
