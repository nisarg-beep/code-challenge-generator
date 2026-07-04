import "react"
import {useState, useEffect} from "react"
import {MCQChallenge} from "./MCQChallenge.jsx";
import {useApi} from "../utils/api.js"

export function ChallengeGenerator() {
    const [challenge, setChallenge] = useState(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)
    const [difficulty, setDifficulty] = useState("easy")
    const [language, setLanguage] = useState("Python") // New State
    const [topic, setTopic] = useState("")             // New State
    const [quota, setQuota] = useState(null)
    const {makeRequest} = useApi()

    useEffect(() => {
        fetchQuota()
    }, [])

    const fetchQuota = async () => {
        try {
            const data = await makeRequest("quota")
            setQuota(data)
        } catch (err) {
            console.log(err)
        }
    }

    const generateChallenge = async () => {
        setIsLoading(true)
        setError(null)

        try {
            // Updated to send difficulty, language, and topic
            const data = await makeRequest("generate-challenge", {
                method: "POST",
                body: JSON.stringify({
                    difficulty,
                    language,
                    topic: topic || "General Concepts" // Fallback if topic is empty
                })
                }
            )
            setChallenge(data)
            fetchQuota()
        } catch (err) {
            setError(err.message || "Failed to generate challenge.")
        } finally {
            setIsLoading(false)
        }
    }

    const getNextResetTime = () => {
        if (!quota?.last_reset_data) return null
        const resetDate = new Date(quota.last_reset_data)
        resetDate.setHours(resetDate.getHours() + 24)
        return resetDate
    }

    return <div className="challenge-container">
        <h2>Coding Challenge Generator</h2>

        {/* 1. Language Dropdown */}
        <div className="input-group">
            <label htmlFor="language">Select Language</label>
            <select
                id="language"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                disabled={isLoading}
            >
                <option value="Python">Python</option>
                <option value="Java">Java</option>
                <option value="C">C</option>
                <option value="C++">C++</option>
                <option value="JavaScript">JavaScript</option>
            </select>
        </div>

        {/* 2. Topic Text Input */}
        <div className="input-group">
            <label htmlFor="topic">Topic (e.g., Recursion, Pointers)</label>
            <input
                id="topic"
                type="text"
                placeholder="What do you want to study?"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                disabled={isLoading}
            />
        </div>

        {/* 3. Difficulty Selector */}
        <div className="difficulty-selector">
            <label htmlFor="difficulty">Select Difficulty</label>
            <select
                id="difficulty"
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                disabled={isLoading}
            >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
            </select>
        </div>

        <button
            onClick={generateChallenge}
            disabled={isLoading}
            className="generate-button"
        >
            {isLoading ? "Generating..." : "Generate Challenge"}
        </button>

        {error && <div className="error-message">
            <p>{error}</p>
        </div>}

        {challenge && <MCQChallenge challenge={challenge}/>}
    </div>
}