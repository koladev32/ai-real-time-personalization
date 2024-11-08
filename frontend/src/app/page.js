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
  const [categories, setCategories] = useState([]);
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

  const [recommendations, setRecommendations] = useState([]);

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

  useEffect(() => {
    async function fetchRecommendations() {
      try {
        const params = {
          ids: "366928,366929,210,169",
        }
        const data = await fetchFromAPI("/products", {params});
        setRecommendations(data.products);
      } catch (error) {
        console.error("Failed to fetch recommendations:", error);
      }
    }
    fetchRecommendations();
  }, []);

  useEffect(() => {
    async function fetchCategories() {
      try {
        const data = await fetchFromAPI("/categories/top_products");
        setCategories(data);
      } catch (error) {
        console.error("Failed to fetch categories:", error);
      }
    }
    fetchCategories();
  }, []);

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
            <div className="flex flex-col w-full">
              <div className="w-10/12 mx-auto">
              <div className="mb-8">
                    <h2 className="text-2xl mb-4 font-semibold">
                    Items You May Love Based on Your Recent Interactions
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-4 gap-3">
                      {recommendations?.slice(0,4).map((product) => (
                        <div>
                          <ProductCard
                            key={product.id}
                            product={product}
                            categoryView
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                {categories.slice(0, 1).map((category) => (
                  <div key={category.id} className="mb-8">
                    <h2 className="text-2xl mb-4">
                      <span className="font-semibold">{category.category_name}</span> - Popular among our customers
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-4 gap-3">
                      {category.products.slice(0, 4).map((product) => (
                        <div>
                          <ProductCard
                            key={product.id}
                            product={product}
                            categoryView
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              <main className="w-10/12 mx-auto flex flex-row space-x-4">
                <div className="w-full">
                  <h2 className="text-2xl font-semibold mb-4">
                    Recent products
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-4 gap-3">
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
              </main>
            </div>
          </div>
        </div>
      </main>
      {isCartOpen && (
        <CartPanel cart={cart} onClose={() => setIsCartOpen(false)} />
      )}
    </>
  );
}
