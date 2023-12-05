'use client';

import toast from 'react-hot-toast';
import Logfile from '../components/logfile';
import { useState } from 'react';

export default function Clean() {
    const [logfile, setLogfile] = useState(null);
    const [logs, setLogs] = useState([]);

    const cleanData = async () => {
        const res = await fetch('http://localhost:8000/tasks/fbref/clean', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                competition: 'Bundesliga',
            }),
        });

        if (!res.ok) {
            toast.error("Something went wrong during data cleaning request!");
            return;
        }

        const loadingToast = toast.loading('Cleaning data...');

        const data = await res.json();
        const logfile = data.logfile;
        setLogfile(logfile);

        const source = new EventSource(`http://localhost:8000/logfiles/stream?logfile=${logfile}`);
        source.onmessage = function (event) {
            const json = JSON.parse(event.data);
            console.log(json);
            if (json.done) {
                source.close();
                toast.success('Data cleaned!', {
                    id: loadingToast,
                });
            }
            setLogs((logs) => [...logs, json.data]);
        };
    };

    return (
        <main className="p-4">
            <label for="competition">Choose a competition:</label>
            <select
                id="competition"
                className="rounded-sm border border-gray-500 bg-white p-2"
            >
                <option value="Bundesliga">Bundesliga</option>
            </select>
            <button onClick={cleanData} className="bg-green-300 px-4 py-2">
                Clean
            </button>
            {logfile && <Logfile logfile={logfile} logs={logs} />}
        </main>
    );
}
