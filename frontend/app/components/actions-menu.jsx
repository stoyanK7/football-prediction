'use client';
import Image from 'next/image';
import Link from 'next/link';

function HorizontalLine() {
    return <div className="h-[2px] w-10 self-center bg-gray-200"></div>;
}

function Action({ name, src, href }) {
    return (
        <Link href={href}>
            <div className="rounded-lg p-4 hover:cursor-pointer hover:bg-gray-100">
                <div className="h-20 w-20 overflow-hidden rounded-full border-2 border-gray-300 bg-white p-4">
                    <Image
                        src={src}
                        alt={name}
                        layout="responsive"
                        width={200}
                        height={200}
                    />
                </div>
                <p class="text-center">{name}</p>
            </div>
        </Link>
    );
}

import { useState } from 'react';
import { FaArrowUp, FaArrowDown } from 'react-icons/fa';

export default function ActionsMenu() {
    const [isNavbarOpen, setIsNavbarOpen] = useState(true);

    const toggleNavbar = () => {
        setIsNavbarOpen(!isNavbarOpen);
    };

    return (
        <div>
            <nav
                className={`flex justify-center border-b-2 border-gray-300 p-4 ${
                    isNavbarOpen ? '' : 'hidden'
                }`}
            >
                <Action
                    name="Crawl"
                    src="/images/web-crawler.png"
                    href="/crawl"
                />
                <Action
                    name="Scrape"
                    src="/images/scraper.png"
                    href="/scrape"
                />
                <Action name="Clean" src="/images/clean.png" href="/clean" />
                <Action
                    name="Prepare"
                    src="/images/prepare.png"
                    href="/prepare"
                />
                <Action name="Train" src="/images/train.png" href="/train" />
            </nav>
            {/* <div className="mt-2 flex justify-center">
                {isNavbarOpen ? (
                    <div
                        class="flex cursor-pointer items-center justify-center gap-2 rounded-sm bg-gray-400 p-2 text-white"
                        onClick={toggleNavbar}
                    >
                        <FaArrowUp />
                        <FaArrowUp />
                        <FaArrowUp />
                    </div>
                ) : (
                    <div
                        class="flex cursor-pointer items-center justify-center gap-2 rounded-sm bg-gray-400 p-2 text-white"
                        onClick={toggleNavbar}
                    >
                        <FaArrowDown />
                        <FaArrowDown />
                        <FaArrowDown />
                    </div>
                )}
            </div> */}
        </div>
    );
}
