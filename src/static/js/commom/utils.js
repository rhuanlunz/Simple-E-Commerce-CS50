async function sendForm(credsForm, url, redirection_url) {
	const toast = document.querySelector('.toast');
	const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toast);

	// Send user data 
	try {
		const response = await fetch(url, {
			method: "POST",
			body: credsForm
		});

		const text = await response.text();
		const data = JSON.parse(text);

		if (data["message"] == "success") {
			globalThis.location = redirection_url;
		} else {
			document.querySelector(".toast-body").innerHTML = data["message"];
			toastBootstrap.show();

			return data["message"];
		}
	} catch (error) {
		console.error("Error: ", error);
	}
}

