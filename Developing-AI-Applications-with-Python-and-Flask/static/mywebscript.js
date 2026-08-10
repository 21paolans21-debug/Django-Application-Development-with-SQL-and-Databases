function runEmotionAnalysis() {
    const textToAnalyze = document.getElementById("textToAnalyze").value;
    const output = document.getElementById("system_response");

    output.textContent = "Analyzing...";

    fetch(`/emotionDetector?textToAnalyze=${encodeURIComponent(textToAnalyze)}`)
        .then((response) => response.text())
        .then((text) => {
            output.textContent = text;
        })
        .catch(() => {
            output.textContent = "Unable to analyze the text. Please try again.";
        });
}
