import { useState, useEffect } from "react"
import { SignedIn, SignedOut, UserButton } from "@clerk/clerk-react"
import { Outlet, Link, Navigate } from "react-router-dom"

export function Layout() {
    // 1. Initialize state from localStorage
    const [isDark, setIsDark] = useState(() => {
        return localStorage.getItem('theme') === 'dark';
    });

    // 2. Update the HTML class and localStorage whenever isDark changes
    useEffect(() => {
        if (isDark) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    }, [isDark]);

    const toggleTheme = () => setIsDark(!isDark);

    return (
        <div className="app-layout">
            <header className="app-header">
                <div className="header-content">
                    <h1>Code Challenge Generator</h1>
                    <nav>
                        <SignedIn>
                            <Link to="/">Generate Challenge</Link>
                            <Link to="/history">History</Link>

                            {/* Updated Toggle Switch based on Figma design */}
                            <div className="theme-switch-wrapper">
                                <label className="theme-switch" htmlFor="checkbox">
                                    <input
                                        type="checkbox"
                                        id="checkbox"
                                        onChange={toggleTheme}
                                        checked={isDark}
                                    />
                                    <div className="slider round"></div>
                                </label>
                            </div>

                            <UserButton />
                        </SignedIn>
                    </nav>
                </div>
            </header>

            <main className="app-main">
                <SignedOut>
                    <Navigate to="/sign-in" replace />
                </SignedOut>
                <SignedIn>
                    <Outlet />
                </SignedIn>
            </main>
        </div>
    );
}