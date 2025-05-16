document.addEventListener("DOMContentLoaded", function() {
    const courseTitleElement = document.getElementById("course-title");
    const courseDescriptionElement = document.getElementById("course-description");
    const courseCreatorElement = document.getElementById("course-creator");
    const courseCreationDateElement = document.getElementById("course-creation-date");
    const lecturesListContainer = document.getElementById("lectures-list");
    const quizzesContainer = document.getElementById("quizzes-container");
    const forumTopicsContainer = document.getElementById("forum-topics-container");

    const urlParams = new URLSearchParams(window.location.search);
    const courseId = urlParams.get("id");

    function displayCourseDetails(course) {
        if (!course) {
            courseTitleElement.textContent = "المقرر غير موجود.";
            return;
        }
        courseTitleElement.textContent = course.title;
        courseDescriptionElement.textContent = course.description || "لا يوجد وصف متاح.";
        courseCreatorElement.textContent = course.creator || "غير محدد";
        courseCreationDateElement.textContent = new Date(course.creation_date).toLocaleDateString("ar-EG");
    }

    function displayLectures(lectures) {
        lecturesListContainer.innerHTML = ""; // Clear loading message
        if (lectures && lectures.length > 0) {
            lectures.forEach(lecture => {
                const lectureItem = document.createElement("div");
                lectureItem.classList.add("lecture-item");
                lectureItem.innerHTML = `
                    <h4>${lecture.title}</h4>
                    <p>${lecture.description ? lecture.description.substring(0,100) + "..." : ""}</p>
                    <a href="#lecture-${lecture.id}" class="lecture-link">عرض المحاضرة</a>
                `; // Link to actual lecture view page later
                lecturesListContainer.appendChild(lectureItem);
            });
        } else {
            lecturesListContainer.innerHTML = "<p>لا توجد محاضرات متاحة لهذا المقرر حالياً.</p>";
        }
    }

    function displayQuizzes(quizzes) {
        quizzesContainer.innerHTML = "";
        if (quizzes && quizzes.length > 0) {
            quizzes.forEach(quiz => {
                const quizItem = document.createElement("div");
                quizItem.classList.add("quiz-item");
                quizItem.innerHTML = `
                    <h4>${quiz.title}</h4>
                    <p>${quiz.description || ""}</p>
                    <a href="#quiz-${quiz.id}" class="quiz-link">بدء الاختبار</a>
                `; // Link to quiz taking page later
                quizzesContainer.appendChild(quizItem);
            });
        } else {
            quizzesContainer.innerHTML = "<p>لا توجد اختبارات متاحة لهذا المقرر حالياً.</p>";
        }
    }

    function displayForumTopics(topics) {
        forumTopicsContainer.innerHTML = "";
        if (topics && topics.length > 0) {
            topics.forEach(topic => {
                const topicItem = document.createElement("div");
                topicItem.classList.add("forum-topic-item");
                topicItem.innerHTML = `
                    <h4>${topic.title}</h4>
                    <p>أنشأه: ${topic.creator} - آخر مشاركة: ${new Date(topic.last_post_date).toLocaleDateString("ar-EG")}</p>
                    <a href="#forum-topic-${topic.id}" class="topic-link">عرض الموضوع</a>
                `; // Link to forum topic page later
                forumTopicsContainer.appendChild(topicItem);
            });
        } else {
            forumTopicsContainer.innerHTML = "<p>لا توجد مواضيع نقاش متاحة لهذا المقرر حالياً.</p>";
        }
    }

    function fetchCourseData(id) {
        // Fetch Course Details
        fetch(`/api/courses/${id}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    courseTitleElement.textContent = data.error;
                } else {
                    displayCourseDetails(data);
                    // After displaying course details, fetch its lectures, quizzes, and forum topics
                    fetchLecturesForCourse(id);
                    fetchQuizzesForCourse(id);
                    fetchForumTopicsForCourse(id);
                }
            })
            .catch(error => {
                console.error("Error fetching course details:", error);
                courseTitleElement.textContent = "حدث خطأ أثناء تحميل تفاصيل المقرر.";
            });
    }

    function fetchLecturesForCourse(courseId) {
        fetch(`/api/courses/${courseId}/lectures`)
            .then(response => response.json())
            .then(data => {
                if (data.lectures) {
                    displayLectures(data.lectures);
                } else {
                    lecturesListContainer.innerHTML = "<p>لم يتم العثور على محاضرات.</p>";
                }
            })
            .catch(error => {
                console.error("Error fetching lectures:", error);
                lecturesListContainer.innerHTML = "<p>خطأ في تحميل المحاضرات.</p>";
            });
    }

    function fetchQuizzesForCourse(courseId) {
        // Assuming an endpoint like /api/courses/{courseId}/quizzes
        // This endpoint needs to be created in quiz.py or course.py
        fetch(`/api/quizzes?course_id=${courseId}`) // Adjust if your API is different
            .then(response => response.json())
            .then(data => {
                // The quiz API returns { "id": ..., "questions": [...] }
                // We need a list of quizzes for a course. Let's assume the API is /api/quizzes?course_id=X
                // and it returns { "quizzes": [ {quiz1}, {quiz2} ] }
                // For now, I'll adapt to the existing /api/quizzes/<id> which gets a single quiz.
                // This part needs backend adjustment for a list of quizzes by course.
                // As a placeholder, I'll show a message.
                // displayQuizzes(data.quizzes); // This would be ideal
                if(data.quizzes) {
                     displayQuizzes(data.quizzes);
                } else {
                    quizzesContainer.innerHTML = "<p>جاري تطوير عرض الاختبارات الخاصة بالمقرر.</p>";
                }
            })
            .catch(error => {
                console.error("Error fetching quizzes for course:", error);
                quizzesContainer.innerHTML = "<p>خطأ في تحميل اختبارات المقرر.</p>";
            });
    }

    function fetchForumTopicsForCourse(courseId) {
        fetch(`/api/forums/topics?course_id=${courseId}`)
            .then(response => response.json())
            .then(data => {
                if (data.topics) {
                    displayForumTopics(data.topics);
                } else {
                    forumTopicsContainer.innerHTML = "<p>لم يتم العثور على مواضيع نقاش.</p>";
                }
            })
            .catch(error => {
                console.error("Error fetching forum topics for course:", error);
                forumTopicsContainer.innerHTML = "<p>خطأ في تحميل مواضيع النقاش.</p>";
            });
    }

    if (courseId) {
        fetchCourseData(courseId);
    } else {
        courseTitleElement.textContent = "لم يتم تحديد مقرر.";
        lecturesListContainer.innerHTML = "";
        quizzesContainer.innerHTML = "";
        forumTopicsContainer.innerHTML = "";
    }

    // Add login/logout/profile link (similar to courses.js, ideally from a shared auth module)
    const navUl = document.querySelector("header nav ul");
    fetch("/api/check_session")
        .then(response => response.json())
        .then(data => {
            const loginListItem = document.createElement("li");
            if (data.logged_in) {
                const profileLink = document.createElement("a");
                profileLink.href = "#profile"; 
                profileLink.textContent = `ملف ${data.user.username}`;
                loginListItem.appendChild(profileLink);

                const logoutLink = document.createElement("a");
                logoutLink.href = "#logout";
                logoutLink.textContent = "تسجيل الخروج";
                logoutLink.style.marginLeft = "10px";
                logoutLink.addEventListener("click", function(e) {
                    e.preventDefault();
                    fetch("/api/logout", { method: "POST" })
                        .then(res => res.json())
                        .then(logoutData => {
                            alert(logoutData.message);
                            window.location.href = "index.html"; // Redirect to home after logout
                        })
                        .catch(err => console.error("Logout error:", err));
                });
                loginListItem.appendChild(logoutLink);

                if (data.user.is_admin) {
                    const adminListItem = document.createElement("li");
                    const adminLink = document.createElement("a");
                    adminLink.href = "#admin_dashboard";
                    adminLink.textContent = "لوحة التحكم";
                    adminListItem.appendChild(adminLink);
                    navUl.appendChild(adminListItem);
                }

            } else {
                const loginLink = document.createElement("a");
                loginLink.href = "index.html#login-form";
                loginLink.textContent = "تسجيل الدخول";
                loginListItem.appendChild(loginLink);
            }
            navUl.appendChild(loginListItem);
        })
        .catch(error => console.error("Error checking session:", error));
});

