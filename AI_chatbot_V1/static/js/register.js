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


function addMessage(message, type) {

    const div = document.createElement("div");

    div.classList.add(
        type === "user"
            ? "user-message"
            : "bot-message"
    );

    div.textContent = message;

    chatBox.appendChild(div);

    chatBox.scrollTop = chatBox.scrollHeight;
}


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

        input.type = "password";
    }

    else if (step === 4) {

        registerUser();
    }
}


sendButton.addEventListener("click", handleInput);

input.addEventListener("keypress", function(event) {

    if (event.key === "Enter") {
        handleInput();
    }

});


function handleInput() {

    const value = input.value.trim();

    if (!value) {
        return;
    }

    addMessage(value, "user");

    input.value = "";

    if (step === 0) {

        userData.name = value;

        step = 1;

        askNextQuestion();

    }

    else if (step === 1) {

        if (isNaN(value)) {

            addMessage(
                "Please enter your age as a number.",
                "bot"
            );

            return;
        }

        userData.age = value;

        step = 2;

        askNextQuestion();

    }

    else if (step === 2) {

        userData.nationality = value;

        step = 3;

        askNextQuestion();

    }

    else if (step === 3) {

        userData.password = value;

        step = 4;

        askNextQuestion();
    }
}


async function registerUser() {

    addMessage(
        "Creating your account... 🎵",
        "bot"
    );

    const response = await fetch(
        "/register",
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(userData)
        }
    );

    const result = await response.json();

    if (result.success) {

        addMessage(
            "Your account has been created successfully! 🎉",
            "bot"
        );

        setTimeout(() => {
            window.location.href = result.redirect;
        }, 1000);

    }

    else {

        addMessage(
            result.message,
            "bot"
        );

        step = 0;
    }
}