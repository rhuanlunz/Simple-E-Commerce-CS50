async function send(creds) {
	const toast = document.querySelector('.toast');
	const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toast);

	// Send user data 
	try {
		const response = await fetch(globalThis.location.href, {
			method: "POST",
			body: JSON.stringify(creds),
			headers: {
				"Content-Type": "application/json"
			}
		});

		const text = await response.text();
		const data = JSON.parse(text);

		if (data["message"] == "success") {
			globalThis.location = "/";
		} else {
			document.querySelector(".toast-body").innerHTML = data["message"];
			toastBootstrap.show();

			return data["message"];
		}
	} catch (error) {
		console.error("Error: ", error);
	}
	return;
}

const showBtns = document.querySelectorAll(".show");

showBtns.forEach(btn => {
	btn.addEventListener("click", function() {
		const input = this.parentNode.querySelector("input[type='password'], input[type='text']");
		
		if (input.type === "password") {
			input.type = "text";
			this.innerHTML = "visibility";
		} else {
			input.type = "password";
			this.innerHTML = "visibility_off";
		}
	});
});


