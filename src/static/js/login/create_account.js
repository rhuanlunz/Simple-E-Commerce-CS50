document.querySelector("#send").addEventListener("click", async () => {
	// Get user data
	const username = document.querySelector("#username");
	const email = document.querySelector("#email");
	const password = document.querySelector("#password");	
	const confirmation = document.querySelector("#confirmation");

	// Focus missing input fields
	if (!username.value) {
		username.focus();
	}
	else if (!email.value) {
		email.focus();
	}
	else if (!password.value) {
		password.focus();
	}
	else if (!confirmation.value) {
		confirmation.focus();
	}

	// Send user data
	const msg = await send({username: username.value, email: email.value, password: password.value, confirmation: confirmation.value});

	// Handle return messages
	switch(msg) {
		case "Username already exists!":
			username.focus();
			break;
		case "Email already exists!", "Invalid email!":
			email.focus();
			break;
		case "Passwords don't match!":
			confirmation.focus();
			break;
	}
});
