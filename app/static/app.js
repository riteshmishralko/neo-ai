function App() {
    const [screen, setScreen] = React.useState(1);
    const [showDropdown, setShowDropdown] = React.useState(false);
    const [uploading, setUploading] = React.useState(false);

    function handleDownload() {
        alert("Download triggered!"); // Or real download logic
        setShowDropdown(false);
    }
    function handleUploadListClick() {
        setShowDropdown(false); // Hide dropdown
        setScreen(3);           // Show upload panel (Screen 3)
    }

    function handleUpload(file) {
        setUploading(true);
        // Fake "uploading..."
        setTimeout(() => {
        setUploading(false);
        setScreen(2);         // Go back to Screen 2 after upload
        }, 1500);
    }

    // Render screens based on state
    if (screen === 1) {
        return React.createElement(GreetingScreen, {onStart: () => setScreen(2)});
    }
    if (screen === 2) {
        return React.createElement(GreetingScreen2, {
            showDropdown: showDropdown,
            setShowDropdown: setShowDropdown,
            onDownload: handleDownload,
            onUpload: () => { setShowDropdown(false); setScreen(3); },
            onMic: () => setScreen("voice"), 
            onClose: () => setScreen(1)
        });
    }
    if (screen === 3) {
        return React.createElement(GreetingScreen3, {
        onClose: () => setScreen(2),    // If user closes the panel, go back to 2
        onUpload: handleUpload,
        uploading: uploading
        });
    }
    if (screen === "voice") {
        return React.createElement(VoiceConversationUI, {
        userId: "123",
        onBack: () => setScreen(2)
        });
    }
    }
    ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(App));