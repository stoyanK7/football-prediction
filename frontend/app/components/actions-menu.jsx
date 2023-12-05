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

export default function ActionsMenu() {
    return (
        <nav className="flex justify-center border-b-2 border-gray-300 p-4">
            <Action name="Crawl" src="/images/web-crawler.png" href="/crawl" />
            <Action name="Scrape" src="/images/scraper.png" href="/scrape" />
            <Action name="Clean" src="/images/clean.png" href="/clean" />
            <Action name="Prepare" src="/images/prepare.png" href="/prepare" />
            <Action name="Train" src="/images/train.png" href="/train" />
        </nav>
    );
}
