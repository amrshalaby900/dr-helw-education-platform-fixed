document.addEventListener("DOMContentLoaded", function() {
    const courseGridContainer = document.getElementById("course-grid-container");

    function displayCourses(courses) {
        courseGridContainer.innerHTML = ""; // Clear loading message or previous content
        if (courses && courses.length > 0) {
            courses.forEach(course => {
                const courseCard = document.createElement("div");
                courseCard.classList.add("course-card");

                const title = document.createElement("h3");
                title.textContent = course.title;

                const description = document.createElement("p");
                description.textContent = course.description ? course.description.substring(0, 150) + (course.description.length > 150 ? "..." : "") : "لا يوجد وصف متاح حالياً.";

                const creator = document.createElement("p");
                creator.innerHTML = `<strong>المُنشئ:</strong> ${course.creator || "غير محدد"}`;

                const creationDate = document.createElement("p");
                creationDate.innerHTML = `<strong>تاريخ الإنشاء:</strong> ${new Date(course.creation_date).toLocaleDateString("ar-EG")}`;

                const detailsLink = document.createElement("a");
                detailsLink.href = `course_details.html?id=${course.id}`; // Link to a future course details page
                detailsLink.classList.add("details-link");
                detailsLink.textContent = "عرض التفاصيل";

                courseCard.appendChild(title);
                courseCard.appendChild(description);
                courseCard.appendChild(creator);
                courseCard.appendChild(creationDate);
                courseCard.appendChild(detailsLink);
                courseGridContainer.appendChild(courseCard);
            });
        } else {
            courseGridContainer.innerHTML = "<p>لا توجد مقررات دراسية متاحة حالياً.</p>";
        }
    }

    function fetchCourses() {
        fetch("/api/courses") // Assuming this is the endpoint to get all courses
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.courses) {
                    displayCourses(data.courses);
                } else {
                    console.error("No courses array in response:", data);
                    courseGridContainer.innerHTML = "<p>حدث خطأ أثناء تحميل المقررات.</p>";
                }
            })
            .catch(error => {
                console.error("Error fetching courses:", error);
                courseGridContainer.innerHTML = "<p>حدث خطأ أثناء تحميل المقررات. يرجى المحاولة مرة أخرى لاحقاً.</p>";
            });
    }

    // Initial fetch of courses when the page loads
    if (courseGridContainer) {
        fetchCourses();
    }

    // Check login status and update nav (example, adapt from main.js or a shared auth module)
    // This part would typically be in a shared JS file or handled by a framework
    const navUl = document.querySelector("header nav ul");
    fetch("/api/check_session")
        .then(response => response.json())
        .then(data => {
            const loginListItem = document.createElement("li");
            if (data.logged_in) {
                const profileLink = document.createElement("a");
                profileLink.href = "#profile"; // Link to user profile page
                profileLink.textContent = `ملف ${data.user.username}`;
                loginListItem.appendChild(profileLink);

                const logoutLink = document.createElement("a");
                logoutLink.href = "#logout";
                logoutLink.textContent = "تسجيل الخروج";
                logoutLink.style.marginLeft = "10px"; // Add some spacing
                logoutLink.addEventListener("click", function(e) {
                    e.preventDefault();
                    fetch("/api/logout", { method: "POST" })
                        .then(res => res.json())
                        .then(logoutData => {
                            alert(logoutData.message);
                            window.location.reload(); // Reload to reflect logged-out state
                        })
                        .catch(err => console.error("Logout error:", err));
                });
                loginListItem.appendChild(logoutLink);

                if (data.user.is_admin) {
                    const adminListItem = document.createElement("li");
                    const adminLink = document.createElement("a");
                    adminLink.href = "#admin_dashboard"; // Link to admin dashboard
                    adminLink.textContent = "لوحة التحكم";
                    adminListItem.appendChild(adminLink);
                    navUl.appendChild(adminListItem);
                }

            } else {
                const loginLink = document.createElement("a");
                loginLink.href = "index.html#login-form"; // Or a dedicated login page
                loginLink.textContent = "تسجيل الدخول";
                loginListItem.appendChild(loginLink);
            }
            navUl.appendChild(loginListItem);
        })
        .catch(error => console.error("Error checking session:", error));
});


