document.addEventListener("DOMContentLoaded", function() {
    const generateCodeBtn = document.getElementById("generate-code-btn");
    const generatedCodeArea = document.getElementById("generated-code-area");
    const logoutLinkAdmin = document.getElementById("logout-link-admin");

    // Check if user is admin and logged in
    fetch("/api/check_session")
        .then(response => response.json())
        .then(data => {
            if (!data.logged_in || !data.user.is_admin) {
                alert("غير مصرح لك بالوصول إلى هذه الصفحة.");
                window.location.href = "index.html"; // Redirect to homepage
            }
        })
        .catch(error => {
            console.error("Error checking admin session:", error);
            alert("حدث خطأ أثناء التحقق من صلاحيات الدخول.");
            window.location.href = "index.html";
        });

    if (generateCodeBtn) {
        generateCodeBtn.addEventListener("click", function() {
            fetch("/api/admin/generate_code", { method: "POST" }) // Ensure this route exists and is protected
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        generatedCodeArea.textContent = "خطأ: " + data.error;
                        generatedCodeArea.style.color = "red";
                    } else if (data.registration_code) {
                        generatedCodeArea.textContent = `تم توليد الكود بنجاح: ${data.registration_code.code}`;
                        generatedCodeArea.style.color = "green";
                    } else {
                        generatedCodeArea.textContent = "لم يتم إرجاع كود. تحقق من الخادم.";
                        generatedCodeArea.style.color = "orange";
                    }
                    generatedCodeArea.style.display = "block";
                })
                .catch(error => {
                    console.error("Error generating code:", error);
                    generatedCodeArea.textContent = "حدث خطأ أثناء توليد الكود. يرجى المحاولة مرة أخرى.";
                    generatedCodeArea.style.color = "red";
                    generatedCodeArea.style.display = "block";
                });
        });
    }

    if(logoutLinkAdmin) {
        logoutLinkAdmin.addEventListener("click", function(e) {
            e.preventDefault();
            fetch("/api/logout", { method: "POST" })
                .then(res => res.json())
                .then(logoutData => {
                    alert(logoutData.message);
                    window.location.href = "index.html"; // Redirect to home after logout
                })
                .catch(err => {
                    console.error("Logout error:", err);
                    alert("حدث خطأ أثناء تسجيل الخروج.");
                });
        });
    }

    // Placeholder for loading admin stats (e.g., user count, course count)
    const adminStatsSection = document.getElementById("admin-stats");
    if (adminStatsSection) {
        // fetch("/api/admin/stats") // Example endpoint
        // .then(response => response.json())
        // .then(data => {
        //     adminStatsSection.innerHTML = `
        //         <p>إجمالي المستخدمين: ${data.total_users || 0}</p>
        //         <p>إجمالي المقررات: ${data.total_courses || 0}</p>
        //         <p>إجمالي المحاضرات: ${data.total_lectures || 0}</p>
        //     `;
        // })
        // .catch(error => {
        //     console.error("Error fetching admin stats:", error);
        //     adminStatsSection.innerHTML = "<p>لم نتمكن من تحميل الإحصائيات.</p>";
        // });
        adminStatsSection.innerHTML = "<p>سيتم عرض الإحصائيات هنا قريباً.</p>"; // Placeholder
    }

    // Placeholder for loading user list for management
    const userManagementSection = document.getElementById("user-management").querySelector("p");
    if (userManagementSection) {
        userManagementSection.textContent = "سيتم عرض قائمة المستخدمين وخيارات الإدارة هنا قريباً.";
    }

    // Placeholder for loading course list for management
    const courseManagementSection = document.getElementById("course-management").querySelector("p");
    if (courseManagementSection) {
        courseManagementSection.textContent = "سيتم عرض قائمة المقررات وخيارات الإدارة هنا قريباً.";
    }

});

