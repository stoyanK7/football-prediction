export default function Logfile({ logfile, logs }) {
    return (
        <div class="rounded-md border border-gray-400 font-mono text-xs">
            <div className="rounded-t-md  border border-b-gray-400 bg-gray-100 p-4 text-center">
                <p className="font-bold">Logfile</p>
                <p>{logfile}</p>
            </div>
            <div>
                {logs && logs.map((log, index) => (
                    <div className="grid grid-cols-[auto_1fr] gap-4" key={index}>
                        <div className="w-10 select-none text-right text-gray-500">
                            {index}
                        </div>
                        <div>{log}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}
