document.addEventListener("DOMContentLoaded", function() {
    const loginForm = document.getElementById("login-form");
    const registrationForm = document.getElementById("registration-form"); 
    const navUl = document.querySelector("header nav ul");
    const userSpecificNavContainer = document.getElementById("user-specific-nav");

    function updateNavigation(userData) {
        let targetNavArea = userSpecificNavContainer;
        if (!targetNavArea) {
            targetNavArea = navUl.querySelector("#user-specific-nav-item");
            if (!targetNavArea) {
                targetNavArea = document.createElement("li");
                targetNavArea.id = "user-specific-nav-item";
                navUl.appendChild(targetNavArea);
            }
        }
        targetNavArea.innerHTML = ""; // Clear previous links

        if (userData && userData.logged_in) {
            const welcomeText = document.createElement("span");
            welcomeText.textContent = `مرحباً، ${userData.user.username}`;
            welcomeText.style.marginRight = "15px";
            welcomeText.style.color = "#fff"; 
            targetNavArea.appendChild(welcomeText);

            if (userData.user.is_admin) {
                const adminLink = document.createElement("a");
                adminLink.href = "admin_dashboard.html";
                adminLink.textContent = "لوحة التحكم";
                adminLink.style.marginRight = "10px";
                targetNavArea.appendChild(adminLink);
            }

            const logoutLink = document.createElement("a");
            logoutLink.href = "#logout";
            logoutLink.textContent = "تسجيل الخروج";
            logoutLink.addEventListener("click", function(e) {
                e.preventDefault();
                fetch("/api/logout", { method: "POST", credentials: "include" })
                    .then(res => res.json())
                    .then(data => {
                        alert(data.message);
                        checkSessionStatus(); 
                        if (window.location.pathname.includes("admin_dashboard.html") || window.location.pathname.includes("courses.html")) {
                            window.location.href = "index.html";
                        }
                    })
                    .catch(err => console.error("Logout error:", err));
            });
            targetNavArea.appendChild(logoutLink);

        } else {
            const loginLink = document.createElement("a");
            loginLink.href = "index.html#login-section"; 
            loginLink.textContent = "تسجيل الدخول";
            targetNavArea.appendChild(loginLink);
        }
    }

    function checkSessionStatus() {
        fetch("/api/check_session", { credentials: "include" })
            .then(response => response.json())
            .then(data => {
                updateNavigation(data);
            })
            .catch(error => {
                console.error("Error checking session:", error);
                updateNavigation(null); 
            });
    }

    if (loginForm) {
        loginForm.addEventListener("submit", function(event) {
            event.preventDefault();
            const username = document.getElementById("login-username").value;
            const password = document.getElementById("login-password").value;
            
            fetch("/api/login", { 
                method: "POST", 
                body: JSON.stringify({ identifier: username, password: password }), 
                headers: { "Content-Type": "application/json" },
                credentials: "include" // Added credentials include
            })
            .then(response => {
                if (!response.ok) {
                    // Try to parse error response, or use statusText
                    return response.json().catch(() => ({ error: response.statusText, message: `HTTP error! status: ${response.status}` }));
                }
                return response.json();
            })
            .then(data => {
                if(data.message === "تم تسجيل الدخول بنجاح." && data.user) {
                    alert(data.message);
                    checkSessionStatus(); 
                    if (data.user.is_admin) {
                        window.location.href = "admin_dashboard.html"; 
                    } else {
                        window.location.href = "courses.html"; 
                    }
                } else {
                    alert("خطأ في تسجيل الدخول: " + (data.error || data.message || "بيانات غير صحيحة."));
                }
            })
            .catch(error => {
                console.error("Login Error:", error);
                alert("حدث خطأ أثناء محاولة تسجيل الدخول: " + error.message);
            });
        });
    }

    if (registrationForm) {
        registrationForm.addEventListener("submit", function(event) {
            event.preventDefault();
            const regUsername = document.getElementById("reg-username").value;
            const regPassword = document.getElementById("reg-password").value;
            const regEmail = document.getElementById("reg-email").value;
            const registrationCode = document.getElementById("reg-code").value;

            fetch("/api/register", {
                method: "POST",
                body: JSON.stringify({
                    username: regUsername,
                    password: regPassword,
                    email: regEmail,
                    registration_code: registrationCode
                }),
                headers: { "Content-Type": "application/json" },
                credentials: "include" // Added credentials include for consistency, though maybe not strictly needed for register
            })
            .then(response => response.json())
            .then(data => {
                if (data.message === "تم تسجيل المستخدم بنجاح.") {
                    alert(data.message + " يمكنك الآن تسجيل الدخول.");
                    registrationForm.reset();
                    document.getElementById("login-section").scrollIntoView();
                } else {
                    alert("خطأ في التسجيل: " + (data.error || data.message || "فشل التسجيل."));
                }
            })
            .catch(error => {
                console.error("Registration Error:", error);
                alert("حدث خطأ أثناء محاولة التسجيل.");
            });
        });
    }

    checkSessionStatus();

});
