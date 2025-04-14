import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
    const location = useLocation();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);
    const navListRef = useRef(null);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 20);
        };
        
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    useEffect(() => {
        if (isMenuOpen && navListRef.current) {
            const menuHeight = navListRef.current.scrollHeight;
            document.documentElement.style.setProperty('--menu-height', `${menuHeight}px`);
            document.body.classList.add('menu-open');
        } else {
            document.body.classList.remove('menu-open');
        }
    }, [isMenuOpen]);

    const navLinks = [
        { to: '/', label: 'Presentation' },
        { to: '/prediction', label: 'Prediction' },
        { to: '/realtime', label: 'Stream Session' },
    ];

    const toggleMenu = () => {
        setIsMenuOpen(!isMenuOpen);
    };

    const handleLinkClick = () => {
        if (window.innerWidth <= 480) {
            setIsMenuOpen(false);
        }
    };

    return (
        <nav className={`navbar ${scrolled ? 'navbar-scrolled' : ''}`}>
            <div className="navbar-container">
                <div className="hamburger" onClick={toggleMenu}>
                    <span className={`hamburger-line ${isMenuOpen ? 'open' : ''}`}></span>
                    <span className={`hamburger-line ${isMenuOpen ? 'open' : ''}`}></span>
                    <span className={`hamburger-line ${isMenuOpen ? 'open' : ''}`}></span>
                </div>
                
                <ul ref={navListRef} className={`nav-list ${isMenuOpen ? 'nav-open' : ''}`}>
                    {navLinks.map((link) => (
                        <li key={link.to} className="nav-item">
                            <Link
                                to={link.to}
                                className={`nav-link ${location.pathname === link.to ? 'active' : ''}`}
                                onClick={handleLinkClick}
                            >
                                <span className="nav-link-text">{link.label}</span>
                            </Link>
                        </li>
                    ))}
                </ul>
            </div>
        </nav>
    );
};

export default Navbar;