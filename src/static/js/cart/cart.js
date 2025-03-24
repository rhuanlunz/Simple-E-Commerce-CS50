const removeItemBtns = document.querySelectorAll(".removeItem");

removeItemBtns.forEach((btn) => {
	btn.addEventListener("click", async function() {
		const json = JSON.stringify({"product_id": this.parentNode.parentNode.parentNode.parentNode.id});
		
		await sendJson(json, "/user/cart/remove");

		globalThis.location.reload();
	});
});


