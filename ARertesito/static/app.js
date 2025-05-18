const apiBaseUrl = "http://127.0.0.1:8000";

async function fetchProducts() {
    const response = await fetch(`${apiBaseUrl}/products/`);
    const products = await response.json();
    const productList = document.getElementById("products");
    productList.innerHTML = "";
    products.forEach(product => {
        const li = document.createElement("li");
        li.textContent = `Termék: ${product.name || product.url}, Ár: ${product.current_price || "N/A"}, Célár: ${product.target_price}`;

        // Törlés gomb
        const delBtn = document.createElement("button");
        delBtn.textContent = "Törlés";
        delBtn.style.marginLeft = "10px";
        delBtn.onclick = async () => {
            if (confirm("Biztosan törlöd ezt a terméket?")) {
                await deleteProduct(product.id);
                await fetchProducts();
            }
        };
        li.appendChild(delBtn);

        productList.appendChild(li);
    });
}

async function deleteProduct(productId) {
    await fetch(`${apiBaseUrl}/products/${productId}`, {
        method: "DELETE"
    });
}


async function addProduct() {
    const addButton = document.getElementById("add-button");
    const url = document.getElementById("product-url").value;
    const targetPrice = document.getElementById("target-price").value;
    const notifyInterval = document.getElementById("notify-interval").value;
    const useremail = document.getElementById("useremail").value;

    if (!url) {
        alert("Az URL mező kitöltése kötelező!!!");
        return;
    }
    // URL validáció
    let validUrl = false;
    try {
        const u = new URL(url);
        validUrl = u.protocol === "http:" || u.protocol === "https:";
    } catch (e) {
        validUrl = false;
    }
    if (!validUrl) {
        alert("Kérlek, adj meg egy érvényes webcímet (URL-t)!");
        return;
    }
    if (!useremail) {
        alert("Az Email mező kitöltése kötelező!!!");
        return;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!useremail || !emailPattern.test(useremail)) {
        alert("Kérlek, adj meg egy érvényes email címet!");
        return;
    }

    // Gomb állapot kezelése
    const originalText = addButton.innerHTML; 
    addButton.disabled = true;
    addButton.classList.add("loading");
    addButton.innerHTML = '<span class="spinner"></span> Feldolgozás...';

    try {
        const response = await fetch(`${apiBaseUrl}/products/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                url: url,
                target_price: parseFloat(targetPrice) || 0.0,
                name: null,
                notify_interval_minutes: parseInt(notifyInterval) || 1440,
                useremail: useremail || null
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ismeretlen hiba történt');
        }

        await response.json();
        document.getElementById("product-url").value = "";
        document.getElementById("target-price").value = "";
        document.getElementById("notify-interval").value = "";
        await fetchProducts();
        alert("Termék sikeresen hozzáadva!");
    } catch (error) {
        alert(`Hiba történt: ${error.message}`);
    } finally {
        addButton.disabled = false;
        addButton.classList.remove("loading");
        addButton.innerHTML = originalText;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    fetchProducts();
    const addButton = document.getElementById("add-button");
    if (addButton) {
        addButton.addEventListener("click", addProduct);
    }
});