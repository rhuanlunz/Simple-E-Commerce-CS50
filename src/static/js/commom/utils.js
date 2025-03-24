async function sendForm(form, url) {
	try {
		const response = await fetch(url, {
			method: "POST",
			body: form
		});

		const text = await response.text();
		const data = JSON.parse(text);

		return data;
	} catch (error) {
		console.error("Error: ", error);
	}
}

async function sendJson(json, url) {
	try {
		const response = await fetch(url, {
			method: "POST",
			body: json,
			headers: {
				"Content-Type": "application/json"
			}
		})

		const text = await response.text();
		const data = JSON.parse(text);

		return data;
	} catch (error) {
		console.error("Error: ", error);
	}
}

function notify(type, message) {
	const toast = document.querySelector('.toast');
	const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toast);

	toast.classList.remove("text-bg-success");
	toast.classList.remove("text-bg-danger");

	if (type === "success") {
		toast.classList.add("text-bg-success");
	}
	else if (type === "error") {
		toast.classList.add("text-bg-danger");
	}

	document.querySelector(".toast-body").innerHTML = message;
	toastBootstrap.show();
}
