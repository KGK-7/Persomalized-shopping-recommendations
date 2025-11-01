const API_LOGIN_URL = "http://127.0.0.1:8000/login";
const API_VIEW_PRODUCT = "http://127.0.0.1:8000/view_product";
const API_ADD_TO_CART = "http://127.0.0.1:8000/add_to_cart";
const grid = document.getElementById("product-grid");
const message = document.getElementById("message");
const loginContainer = document.getElementById("login-container");
const loginBtn = document.getElementById("loginBtn");
const loginMessage = document.getElementById("loginMessage");
const userActions = document.getElementById("user-actions");
const logoutBtn = document.getElementById("logoutBtn");
const userNameDisplay = document.getElementById("user-name");

function getLoggedInUser() {
  return {
    id: parseInt(localStorage.getItem("user_id")),
    name: localStorage.getItem("user_name")
  };
}

function checkLoginStatus() {
  const user = getLoggedInUser();
  if (user.id) {
    loginContainer.style.display = "none";
    userActions.style.display = "block";
    userNameDisplay.textContent = `Hello, ${user.name}`;
    fetchRecommendations();
  } else {
    loginContainer.style.display = "block";
    userActions.style.display = "none";
    grid.innerHTML = "";
    grid.style.display = "none";
    message.textContent = "";
  }
}
loginBtn.addEventListener("click", async () => {
  const email = document.getElementById("email").value.trim();
  if (!email) {
    loginMessage.textContent = "Please enter your email.";
    return;
  }

  try {
    const res = await fetch(API_LOGIN_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email })
    });

    if (!res.ok) throw new Error("Invalid email");

    const data = await res.json();
    localStorage.setItem("user_id", data.user_id);
    localStorage.setItem("user_name", data.name);

    loginMessage.style.color = "green";
    loginMessage.textContent = "Login successful!";
    checkLoginStatus();
  } catch (err) {
    loginMessage.style.color = "red";
    loginMessage.textContent = "Login failed: " + err.message;
  }
});
logoutBtn.addEventListener("click", () => {
  localStorage.removeItem("user_id");
  localStorage.removeItem("user_name");
  checkLoginStatus();
});

async function fetchRecommendations(productId = null) {
  const user = getLoggedInUser();
  if (!user.id) return;

  // If no productId provided, fetch first product dynamically
  if (!productId) {
    try {
      const resAll = await fetch("http://127.0.0.1:8000/get_all_products"); // new endpoint
      const allProducts = await resAll.json();
      if (allProducts.length === 0) {
        message.textContent = "No products available.";
        return;
      }
      productId = allProducts[0].product_id; // first product
    } catch (err) {
      console.error(err);
      message.textContent = "Failed to fetch products.";
      return;
    }
  }

  const requestData = { user_id: user.id, product_id: productId };

  try {
    message.textContent = "Loading recommendations...";
    grid.innerHTML = "";
    grid.style.display = "none";

    const res = await fetch(API_VIEW_PRODUCT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestData)
    });

    if (!res.ok) throw new Error(`Server Error: ${res.status}`);
    const data = await res.json();
    const products = data.recommended_products || [];

    renderProducts(products);
  } catch (err) {
    console.error(err);
    message.textContent = "Failed to load recommendations.";
  }
}

function renderProducts(products) {
  grid.innerHTML = "";

  if (products.length === 0) {
    message.textContent = "No recommendations found.";
    grid.style.display = "none";
    return;
  }

  message.style.display = "none";
  grid.style.display = "grid";

  products.forEach((p) => {
    const card = document.createElement("div");
    card.className = "card";

    card.innerHTML = `
      <img src="${p.image_url}" alt="${p.name}" class="product-img">
      <div class="card-body">
        <h2 class="product-name">${p.name}</h2>
        <p class="product-price">₹${p.price || '-'}</p>
        <button class="view-btn">View Product</button>
        <button class="add-cart-btn">Add to Cart</button>
      </div>
    `;

    // View Product Button
    card.querySelector(".view-btn").onclick = () => {
      fetchRecommendations(p.id); // fetch recommendations for clicked product
    };

    card.querySelector(".add-cart-btn").onclick = async () => {
      try {
        const user = getLoggedInUser();
        const res = await fetch(API_ADD_TO_CART, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: user.id, product_id: p.id, quantity: 1 })
        });

        if (!res.ok) throw new Error(`Server Error: ${res.status}`);
        const data = await res.json();
        alert("Added to cart!\nCart recommendations: " + JSON.stringify(data.cart_recommendations));
      } catch (err) {
        console.error(err);
        alert("Failed to add to cart: " + err.message);
      }
    };

    grid.appendChild(card);
  });
}
checkLoginStatus();
