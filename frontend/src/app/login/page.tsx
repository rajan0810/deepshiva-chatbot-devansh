"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Leaf, Lock, Mail, Loader2, ArrowRight } from "lucide-react";

export default function LoginPage() {
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError("");

        try {
            const formData = new FormData();
            formData.append("username", email);
            formData.append("password", password);

            const res = await fetch("/api/auth/login", {
                method: "POST",
                body: formData,
            });

            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || "Login failed");
            }

            const data = await res.json();
            localStorage.setItem("token", data.access_token);
            router.push("/");
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#FDFCF8] p-4 font-sans relative overflow-hidden">
            
            {/* Background Decorative Elements */}
            <div className="absolute top-0 left-0 w-64 h-64 bg-[#3A5A40]/5 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2"></div>
            <div className="absolute bottom-0 right-0 w-96 h-96 bg-[#A3B18A]/10 rounded-full blur-3xl translate-x-1/3 translate-y-1/3"></div>

            <div className="w-full max-w-md z-10">
                {/* Header Logo Area */}
                <div className="flex flex-col items-center mb-8">
                    <div className="w-16 h-16 bg-[#3A5A40] rounded-2xl flex items-center justify-center shadow-lg shadow-[#3A5A40]/20 mb-6 rotate-3 transition-transform hover:rotate-0">
                        <Leaf className="w-8 h-8 text-[#F2E8CF]" strokeWidth={2} />
                    </div>
                    <h1 className="text-3xl font-serif font-bold text-stone-800 text-center">Welcome to DeepShiva</h1>
                    <p className="text-stone-500 mt-2 text-center">Your Ayurvedic path to wellness begins here.</p>
                </div>

                {/* Login Card */}
                <div className="bg-white rounded-3xl shadow-xl shadow-stone-200/50 p-8 border border-stone-100">
                    <form onSubmit={handleLogin} className="space-y-6">
                        {error && (
                            <div className="bg-red-50 border border-red-100 text-red-600 p-3 rounded-xl text-sm text-center font-medium">
                                {error}
                            </div>
                        )}

                        <div className="space-y-2">
                            <label className="text-sm font-bold text-stone-700 ml-1">Email Address</label>
                            <div className="relative group">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-stone-400 group-focus-within:text-[#3A5A40] transition-colors" />
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full bg-stone-50 border border-stone-200 rounded-xl py-3.5 pl-12 pr-4 text-stone-800 placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-[#3A5A40]/20 focus:border-[#3A5A40] transition-all"
                                    placeholder="you@example.com"
                                    required
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-bold text-stone-700 ml-1">Password</label>
                            <div className="relative group">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-stone-400 group-focus-within:text-[#3A5A40] transition-colors" />
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-stone-50 border border-stone-200 rounded-xl py-3.5 pl-12 pr-4 text-stone-800 placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-[#3A5A40]/20 focus:border-[#3A5A40] transition-all"
                                    placeholder="••••••••"
                                    required
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-[#3A5A40] hover:bg-[#2F4A33] text-white font-bold py-4 rounded-xl transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 flex items-center justify-center gap-2 group"
                        >
                            {isLoading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <>
                                    Sign In 
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </button>
                    </form>
                </div>

                {/* Footer */}
                <div className="mt-8 text-center">
                    <p className="text-stone-500">
                        Don't have an account?{" "}
                        <Link href="/signup" className="text-[#3A5A40] font-bold hover:underline hover:text-[#2F4A33] transition-colors">
                            Start your journey
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}