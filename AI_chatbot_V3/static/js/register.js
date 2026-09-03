const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

let step = 0;

let userData = {
    name: "",
    age: "",
    nationality: "",
    password: ""
};


/* =========================================================
   SCROLL CHAT TO BOTTOM
   ========================================================= */

function scrollChatToBottom() {

    if (!chatBox) {
        return;
    }

    requestAnimationFrame(() => {

        chatBox.scrollTop =
            chatBox.scrollHeight;

    });
}


/* =========================================================
   ADD MESSAGE
   ========================================================= */

function addMessage(message, type) {

    if (!chatBox) {
        return;
    }

    const div =
        document.createElement("div");


    div.classList.add(
        type === "user"
            ? "user-message"
            : "bot-message"
    );


    div.textContent =
        message;


    chatBox.appendChild(
        div
    );


    scrollChatToBottom();
}


/* =========================================================
   ASK NEXT QUESTION
   ========================================================= */

function askNextQuestion() {

    if (step === 1) {

        addMessage(
            "Nice to meet you, " +
            userData.name +
            "! 😊 How old are you?",
            "bot"
        );

    }

    else if (step === 2) {

        addMessage(
            "Great! What is your nationality?",
            "bot"
        );

    }

    else if (step === 3) {

        addMessage(
            "Almost done! Please create a password for your account.",
            "bot"
        );


        /*
         * Change input to password field
         * so the password is hidden while typing.
         */

        input.type = "password";

        input.placeholder =
            "Enter your password...";

    }

    else if (step === 4) {

        registerUser();

    }
}


/* =========================================================
   SEND BUTTON
   ========================================================= */

if (sendButton) {

    sendButton.addEventListener(
        "click",
        handleInput
    );

}


/* =========================================================
   ENTER KEY
   ========================================================= */

if (input) {

    input.addEventListener(
        "keypress",
        function(event) {

            if (event.key === "Enter") {

                event.preventDefault();

                handleInput();

            }

        }
    );

}


/* =========================================================
   HANDLE USER INPUT
   ========================================================= */

function handleInput() {

    if (!input) {
        return;
    }


    const value =
        input.value.trim();


    /*
     * Don't allow empty messages.
     */

    if (!value) {
        return;
    }


    /*
     * Display user's message.
     */

    addMessage(
        value,
        "user"
    );


    /*
     * Clear input immediately.
     */

    input.value = "";


    /* =====================================================
       STEP 0 → NAME
       ===================================================== */

    if (step === 0) {

        userData.name =
            value;


        step = 1;


        askNextQuestion();

    }


    /* =====================================================
       STEP 1 → AGE
       ===================================================== */

    else if (step === 1) {

        /*
         * Check that age contains only a number.
         */

        if (
            isNaN(value) ||
            Number(value) <= 0
        ) {

            addMessage(
                "Please enter your age as a number.",
                "bot"
            );

            return;
        }


        userData.age =
            value;


        step = 2;


        askNextQuestion();

    }


    /* =====================================================
       STEP 2 → NATIONALITY
       ===================================================== */

    else if (step === 2) {

        userData.nationality =
            value;


        step = 3;


        askNextQuestion();

    }


    /* =====================================================
       STEP 3 → PASSWORD
       ===================================================== */

    else if (step === 3) {

        userData.password =
            value;


        step = 4;


        askNextQuestion();

    }

}


/* =========================================================
   REGISTER USER
   ========================================================= */

async function registerUser() {

    /*
     * Prevent multiple registration requests.
     */

    if (sendButton) {

        sendButton.disabled =
            true;

    }


    addMessage(
        "Creating your account... 🎵",
        "bot"
    );


    try {

        const response =
            await fetch(
                "/register",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            userData
                        )
                }
            );


        const result =
            await response.json();


        /* =================================================
           SUCCESS
           ================================================= */

        if (result.success) {

            addMessage(
                "Your account has been created successfully! 🎉",
                "bot"
            );


            scrollChatToBottom();


            setTimeout(
                () => {

                    window.location.href =
                        result.redirect;

                },
                1000
            );

        }


        /* =================================================
           REGISTRATION FAILED
           ================================================= */

        else {

            addMessage(
                result.message ||
                "Something went wrong while creating your account.",
                "bot"
            );


            /*
             * Start registration again.
             */

            step = 0;


            userData = {
                name: "",
                age: "",
                nationality: "",
                password: ""
            };


            /*
             * Restore normal text input.
             */

            input.type =
                "text";

            input.placeholder =
                "Type your answer...";


            if (sendButton) {

                sendButton.disabled =
                    false;

            }


            scrollChatToBottom();

        }

    }


    /* =====================================================
       NETWORK / SERVER ERROR
       ===================================================== */

    catch (error) {

        console.error(
            "Registration error:",
            error
        );


        addMessage(
            "Something went wrong while creating your account. Please try again.",
            "bot"
        );


        step = 0;


        userData = {
            name: "",
            age: "",
            nationality: "",
            password: ""
        };


        input.type =
            "text";

        input.placeholder =
            "Type your answer...";


        if (sendButton) {

            sendButton.disabled =
                false;

        }


        scrollChatToBottom();

    }

}