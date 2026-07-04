import "react"
import {useState, useEffect} from "react"
import {MCQChallenge} from "../challenge/MCQChallenge.jsx";
import {useApi} from "../utils/api.js";

export function HistoryPanel() {
    const {makeRequest} = useApi()
    const [history, setHistory] = useState([])
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        fetchHistory()
    }, [])

    const fetchHistory = async () => {
        setIsLoading(true)
        setError(null)
        try {
            const data = await makeRequest("my-history")
            // Reversing to show newest first
            setHistory([...data.challenges].reverse())
        } catch (err) {
            setError("Failed to load history.")
        } finally {
            setIsLoading(false)
        }
    }

    const handleClearHistory = async () => {
        if (window.confirm("Are you sure you want to delete all history?")) {
            try {
                await makeRequest("clear-history", { method: "DELETE" });
                setHistory([]);
            } catch (err) {
                alert("Failed to clear history.");
            }
        }
    };

    if (isLoading) return <div className="loading">Loading history...</div>

    return (
        <div className="history-panel">
            <div className="history-header">
                <h2>History</h2>
                {history.length > 0 && (
                    <button className="clear-history-btn" onClick={handleClearHistory}>
                        Clear All
                    </button>
                )}
            </div>

            {history.length === 0 ? (
                <p>No challenge history</p>
            ) : (
                <div className="history-list">
                    {history.map((challenge) => (
                        <div key={challenge.id} className="history-item">
                            {/* We pass the challenge data exactly as it is */}
                            <MCQChallenge
                                challenge={challenge}
                                showExplanation={true}
                            />
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}