export default function Logfile() {
    return (
        <div class="rounded-md border border-gray-400 font-mono text-xs">
            <div className="rounded-t-md  border border-b-gray-400 bg-gray-100 p-4 text-center">
                <p className="font-bold">Logfile</p>
                <p>name of logfile.log</p>
            </div>
            <div>
                <div className="grid grid-cols-[auto_1fr] gap-4">
                    <div className="w-10 select-none text-right text-gray-500">
                        1
                    </div>
                    <div>Text asd</div>
                </div>
            </div>
        </div>
    );
}
