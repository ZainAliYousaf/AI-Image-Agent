import { useState } from "react";
import UploadZone from "./components/UploadZone";
import { processImages } from "./services/api";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {

    const [files, setFiles] = useState([]);
    const [prompt, setPrompt] = useState("");
    const [processing, setProcessing] = useState(false);
    const [results, setResults] = useState([]);

    const handleProcess = async () => {

        if (files.length === 0) {

            alert(
                "Please select at least one image."
            );

            return;
        }

        if (!prompt.trim()) {

            alert(
                "Please describe what you want to do."
            );

            return;
        }

        try {

            setProcessing(true);
            setResults([]);

            const result = await processImages(
                files,
                prompt
            );

            if (
                !result ||
                !result.files ||
                result.files.length === 0
            ) {

                throw new Error(
                    "No output files were generated."
                );
            }

            setResults(
                result.files
            );

        } catch (error) {

            console.error(
                "Agent error:",
                error
            );

            if (error.response) {

                console.error(
                    "Status:",
                    error.response.status
                );

                console.error(
                    "Response:",
                    error.response.data
                );

                if (
                    error.response.status === 429
                ) {

                    alert(
                        "The AI service has reached its current usage limit. Please try again later."
                    );

                } else {

                    alert(
                        `Processing failed.\nStatus: ${error.response.status}`
                    );
                }

            } else {

                alert(
                    "Something went wrong while processing your images."
                );
            }

        } finally {

            setProcessing(false);

        }
    };


    const getDownloadUrl = (file) => {

        return (
            API_URL +
            file.download_url
        );

    };


    const getFileExtension = (filename) => {

        if (!filename) {
            return "FILE";
        }

        const parts = filename.split(".");

        if (parts.length < 2) {
            return "FILE";
        }

        return parts[
            parts.length - 1
        ].toUpperCase();

    };


    const getFileTypeClass = (filename) => {

        const extension =
            getFileExtension(filename).toLowerCase();

        if (extension === "pdf") {
            return "pdf";
        }

        if (
            extension === "jpg" ||
            extension === "jpeg"
        ) {
            return "jpg";
        }

        if (extension === "png") {
            return "png";
        }

        if (extension === "webp") {
            return "webp";
        }

        if (extension === "avif") {
            return "avif";
        }

        return "default";

    };


    return (

        <div className="app">

            {/* =========================================
                HEADER
            ========================================= */}

            <header className="header">

                <h1>
                    AI Image Agent
                </h1>

                <p>
                    Convert, compress and create PDFs with AI
                </p>

            </header>


            <main className="container">

                {/* =========================================
                    UPLOAD
                ========================================= */}

                <UploadZone
                    files={files}
                    setFiles={setFiles}
                />


                {/* =========================================
                    PROMPT
                ========================================= */}

                <div className="prompt-section">

                    <label htmlFor="prompt">
                        What do you want to do?
                    </label>

                    <textarea
                        id="prompt"
                        value={prompt}
                        onChange={(e) =>
                            setPrompt(
                                e.target.value
                            )
                        }
                        placeholder="Example: Convert these images to PNG, compress them below 500 KB and create a PDF."
                        disabled={processing}
                    />

                </div>


                {/* =========================================
                    PROCESS BUTTON
                ========================================= */}

                <button
                    className="process-button"
                    onClick={handleProcess}
                    disabled={processing}
                >

                    {processing ? (

                        <span className="processing-content">

                            <span className="processing-spinner"></span>

                            Processing...

                        </span>

                    ) : (

                        <span className="process-content">

                            <span>
                                ✦
                            </span>

                            Process Images

                        </span>

                    )}

                </button>


                {/* =========================================
                    RESULTS
                ========================================= */}

                {results.length > 0 && (

                    <section className="results-section">

                        <div className="results-heading">

                            <div className="results-success-icon">
                                ✓
                            </div>

                            <div>

                                <h2>
                                    Processing Complete
                                </h2>

                                <p>
                                    Your processed files are ready to download.
                                </p>

                            </div>

                        </div>


                        <div className="results-count">

                            {results.length}{" "}
                            {results.length === 1
                                ? "file"
                                : "files"}{" "}
                            ready

                        </div>


                        <div className="results-list">

                            {results.map(
                                (file, index) => {

                                    const extension =
                                        getFileExtension(
                                            file.filename
                                        );

                                    const typeClass =
                                        getFileTypeClass(
                                            file.filename
                                        );

                                    return (

                                        <div
                                            className={`result-item result-${typeClass}`}
                                            key={`${file.filename}-${index}`}
                                        >

                                            <div className="result-file-info">

                                                <div
                                                    className={`result-file-icon ${typeClass}`}
                                                >

                                                    {extension === "PDF"
                                                        ? "PDF"
                                                        : extension}

                                                </div>


                                                <div className="result-file-details">

                                                    <strong
                                                        title={
                                                            file.filename
                                                        }
                                                    >
                                                        {file.filename}
                                                    </strong>

                                                    <span>
                                                        {extension} file
                                                    </span>

                                                </div>

                                            </div>


                                            <a
                                                className="download-button"
                                                href={
                                                    getDownloadUrl(
                                                        file
                                                    )
                                                }
                                                download={
                                                    file.filename
                                                }
                                            >

                                                <span>
                                                    ↓
                                                </span>

                                                Download

                                            </a>

                                        </div>

                                    );

                                }
                            )}

                        </div>

                    </section>

                )}

            </main>

        </div>
    );
}

export default App;