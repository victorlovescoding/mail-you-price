
const logIn = document.getElementById("logIn");
const signUp = document.getElementById("signUp");
const nameInput = document.getElementById("nameInput");
const formEl = document.querySelector("form");
const loginBtn = document.querySelector("#loginBtn");

function switchToSignUp() {
	logIn.style.backgroundColor = "#F1F2F2";
	signUp.style.backgroundColor = "#ffffff";
	nameInput.style.display = "block";
	formEl.style.marginTop = "1rem";
	formEl.action = "/";
	loginBtn.innerHTML = "Sign up";
}
function switchToLogIn() {
	logIn.style.backgroundColor = "#ffffff";
	signUp.style.backgroundColor = "#F1F2F2";
	nameInput.style.display = "none";
	formEl.action = "/member";
	loginBtn.innerHTML = "Log in";
}
signUp.addEventListener("click", () => {
	switchToSignUp();
});
logIn.addEventListener("click", () => {
	switchToLogIn();
});
const { createApp } = Vue;
createApp({
	data() {
		return {
			message: "Hello Vue!",
		};
	},
	delimiters: ["[[", "]]"],
}).mount("#app");