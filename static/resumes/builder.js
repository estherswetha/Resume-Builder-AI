document.addEventListener("DOMContentLoaded", function () {

    "use strict";

    // ==========================================
    // 1. GET HTML ELEMENTS
    // ==========================================

    const form = document.getElementById("resumeForm");

    if (!form) {
        console.error("Resume form not found.");
        return;
    }

    const sections = Array.from(
        form.querySelectorAll(".form-section")
    );

    const stepButtons = Array.from(
        form.querySelectorAll(".step")
    );

    const nextButton = document.getElementById("nextButton");

    const previousButton = document.getElementById(
        "previousButton"
    );

    const generateButton = document.getElementById(
        "generateButton"
    );

    const saveDraftButton = document.getElementById(
        "saveDraftButton"
    );

    const voiceLanguage = document.getElementById(
        "voiceLanguage"
    );

    const voiceStatus = document.getElementById(
        "voiceStatus"
    );

    let currentStep = 0;

    let recognition = null;

    let activeVoiceButton = null;

    let activeVoiceField = null;


    // ==========================================
    // 2. VOICE STATUS
    // ==========================================

    function updateVoiceStatus(message) {

        if (voiceStatus) {
            voiceStatus.textContent = message;
        }

    }


    // ==========================================
    // 3. STOP VOICE INPUT
    // ==========================================

    function stopVoiceRecognition() {

        const currentRecognition = recognition;

        recognition = null;

        if (activeVoiceButton) {

            activeVoiceButton.classList.remove("listening");

            activeVoiceButton.setAttribute(
                "aria-pressed",
                "false"
            );

        }

        activeVoiceButton = null;

        activeVoiceField = null;

        if (currentRecognition) {

            try {
                currentRecognition.stop();
            } catch (error) {
                // Recognition may already have stopped.
            }

        }

    }


    // ==========================================
    // 4. SHOW STEP
    // ==========================================

    function showStep(stepIndex) {

        if (
            stepIndex < 0 ||
            stepIndex >= sections.length
        ) {
            return;
        }

        stopVoiceRecognition();

        currentStep = stepIndex;

        sections.forEach(function (section, index) {

            section.hidden = index !== currentStep;

            section.classList.toggle(
                "active",
                index === currentStep
            );

        });


        // Update numbered navigation

        stepButtons.forEach(function (button, index) {

            button.classList.toggle(
                "active",
                index === currentStep
            );

            button.classList.toggle(
                "completed",
                index < currentStep
            );

            if (index === currentStep) {

                button.setAttribute(
                    "aria-current",
                    "step"
                );

            } else {

                button.removeAttribute("aria-current");

            }

        });


        // Previous button

        if (previousButton) {

            previousButton.hidden = currentStep === 0;

            previousButton.disabled = currentStep === 0;

        }


        // Next button

        if (nextButton) {

            nextButton.hidden =
                currentStep === sections.length - 1;

        }


        // Generate button

        if (generateButton) {

            generateButton.hidden =
                currentStep !== sections.length - 1;

        }

        // Scroll to the builder

        const builder = document.querySelector(".builder");

        if (builder) {

            builder.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }

    }


    // ==========================================
    // 5. VALIDATE CURRENT STEP
    // ==========================================

    function validateStep(stepIndex) {

        const section = sections[stepIndex];

        if (!section) {
            return true;
        }

        const fields = section.querySelectorAll(
            "input[required], textarea[required], select[required]"
        );

        let firstInvalid = null;

        fields.forEach(function (field) {

            field.classList.remove("field-error");

            if (!field.checkValidity()) {

                field.classList.add("field-error");

                if (!firstInvalid) {
                    firstInvalid = field;
                }

            }

        });


        if (firstInvalid) {

            firstInvalid.focus();

            firstInvalid.reportValidity();

            return false;

        }

        return true;

    }


    // ==========================================
    // 6. NEXT BUTTON
    // ==========================================

    if (nextButton) {

        nextButton.addEventListener("click", function () {

            if (!validateStep(currentStep)) {
                return;
            }

            if (currentStep < sections.length - 1) {

                showStep(currentStep + 1);

            }

        });

    }


    // ==========================================
    // 7. PREVIOUS BUTTON
    // ==========================================

    if (previousButton) {

        previousButton.addEventListener("click", function () {

            if (currentStep > 0) {

                showStep(currentStep - 1);

            }

        });

    }


    // ==========================================
    // 8. CLICK ON NUMBERED STEPS
    // ==========================================

    stepButtons.forEach(function (button, index) {

        button.addEventListener("click", function () {

            // Allow moving backwards

            if (index <= currentStep) {

                showStep(index);

                return;

            }


            // Validate steps before moving forwards

            for (
                let i = currentStep;
                i < index;
                i++
            ) {

                if (!validateStep(i)) {

                    showStep(i);

                    return;

                }

            }

            showStep(index);

        });

    });


    // ==========================================
    // 9. REMOVE FIELD ERRORS WHILE TYPING
    // ==========================================

    form.querySelectorAll(
        "input, textarea, select"
    ).forEach(function (field) {

        field.addEventListener("input", function () {

            if (field.checkValidity()) {

                field.classList.remove("field-error");

            }

        });

        field.addEventListener("change", function () {

            if (field.checkValidity()) {

                field.classList.remove("field-error");

            }

        });

    });


    // ==========================================
    // 10. VOICE INPUT SUPPORT
    // ==========================================

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;


    function startVoiceRecognition(field, button) {

        if (!SpeechRecognition) {

            updateVoiceStatus(
                "Voice input is not supported. Please use Google Chrome or Microsoft Edge."
            );

            return;

        }

        if (!field) {

            updateVoiceStatus(
                "Input field not found."
            );

            return;

        }

        stopVoiceRecognition();

        recognition = new SpeechRecognition();

        recognition.lang = voiceLanguage
            ? voiceLanguage.value
            : "en-IN";

        recognition.continuous = false;

        recognition.interimResults = false;

        recognition.maxAlternatives = 1;

        activeVoiceField = field;

        activeVoiceButton = button;

        button.classList.add("listening");

        button.setAttribute(
            "aria-pressed",
            "true"
        );

        updateVoiceStatus(
            "Listening... Please speak now."
        );


        // Speech result

        recognition.onresult = function (event) {

            const transcript =
                event.results[0][0].transcript;

            if (transcript && activeVoiceField) {

                const existingText =
                    activeVoiceField.value.trim();

                activeVoiceField.value = existingText
                    ? existingText + " " + transcript
                    : transcript;

                activeVoiceField.dispatchEvent(
                    new Event("input", {
                        bubbles: true
                    })
                );

                activeVoiceField.dispatchEvent(
                    new Event("change", {
                        bubbles: true
                    })
                );

                updateVoiceStatus(
                    "Voice text added successfully."
                );

            }

        };


        // Speech errors

        recognition.onerror = function (event) {

            let message =
                "Voice input failed. Please try again.";

            if (event.error === "not-allowed") {

                message =
                    "Microphone permission denied. Allow microphone access.";

            } else if (event.error === "no-speech") {

                message =
                    "No speech detected. Please speak again.";

            } else if (event.error === "network") {

                message =
                    "Network error. Check your internet connection.";

            }

            updateVoiceStatus(message);

        };


        // Speech stopped

        recognition.onend = function () {

            if (activeVoiceButton) {

                activeVoiceButton.classList.remove(
                    "listening"
                );

                activeVoiceButton.setAttribute(
                    "aria-pressed",
                    "false"
                );

            }

            activeVoiceButton = null;

            activeVoiceField = null;

            recognition = null;

        };


        // Start microphone

        try {

            recognition.start();

        } catch (error) {

            stopVoiceRecognition();

            updateVoiceStatus(
                "Unable to start voice input. Please try again."
            );

        }

    }


    // ==========================================
    // 11. CONNECT MICROPHONE TO EACH FIELD
    // ==========================================

    form.querySelectorAll(".voice-btn").forEach(
        function (button) {

            button.setAttribute(
                "aria-pressed",
                "false"
            );

            button.addEventListener("click", function () {

                const wrapper = button.closest(".withvoice");

                const field = wrapper
                    ? wrapper.querySelector(
                        "input, textarea, select"
                    )
                    : null;


                // Stop if clicking the active microphone again

                if (
                    activeVoiceButton === button &&
                    recognition
                ) {

                    stopVoiceRecognition();

                    updateVoiceStatus(
                        "Voice input stopped."
                    );

                    return;

                }

                startVoiceRecognition(field, button);

            });

        }
    );


    // ==========================================
    // 12. CHANGE VOICE LANGUAGE
    // ==========================================

    if (voiceLanguage) {

        voiceLanguage.addEventListener(
            "change",
            function () {

                stopVoiceRecognition();

                updateVoiceStatus(
                    "Voice language changed. Select Voice to speak."
                );

            }
        );

    }


    // ==========================================
    // 13. SAVE DRAFT
    // ==========================================

    if (saveDraftButton) {

        saveDraftButton.addEventListener(
            "click",
            function () {

                stopVoiceRecognition();

                // Normal Django form submission continues.

            }
        );

    }


    // ==========================================
    // 14. GENERATE AI RESUME
    // ==========================================

    if (generateButton) {

        generateButton.addEventListener(
            "click",
            function (event) {

                // Validate all four steps before generation

                for (
                    let i = 0;
                    i < sections.length;
                    i++
                ) {

                    if (!validateStep(i)) {

                        event.preventDefault();

                        showStep(i);

                        return;

                    }

                }

                stopVoiceRecognition();

                generateButton.disabled = true;

                generateButton.textContent =
                    "Generating Your AI Resume...";

            }
        );

    }


    // ==========================================
    // 15. PREVENT ACCIDENTAL ENTER SUBMISSION
    // ==========================================

    form.addEventListener("keydown", function (event) {

        if (
            event.key === "Enter" &&
            event.target.tagName !== "TEXTAREA" &&
            event.target.type !== "submit"
        ) {

            event.preventDefault();

        }

    });


    // ==========================================
    // 16. INITIALIZE RESUME BUILDER
    // ==========================================

    showStep(0);

    updateVoiceStatus(
        SpeechRecognition
            ? "Voice input is ready. Select a language and press Voice."
            : "Voice input is unavailable in this browser. Use Chrome or Edge."
    );

    console.log(
        "ResumeGen.AI Builder loaded successfully."
    );

});