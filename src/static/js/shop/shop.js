document.querySelectorAll(".addCart").forEach((btn) => {
	btn.addEventListener("click", async function() {
		const json = JSON.stringify({"product_id": this.parentNode.parentNode.parentNode.parentNode.id});
		
		const msg = await sendJson(json, "/user/cart/add");

		notify(msg["type"], msg["message"]);
	});
});

document.querySelector("#search").addEventListener("input", function() {
	const products = document.querySelectorAll(".card-title");

	if (this.value !== "") {
		const search = this.value.charAt(0).toUpperCase() + this.value.slice(1);

		for (prod of products) {
			if (!prod.innerHTML.includes(search)) {
				prod.parentNode.parentNode.style.display = "none";
			}
		}
	} else {
		for (prod of products) {
			prod.parentNode.parentNode.style.display = "";
		}
	}
});
