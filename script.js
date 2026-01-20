document.addEventListener('DOMContentLoaded', () => {
    const searchBtn = document.getElementById('searchBtn');
    const bookInput = document.getElementById('bookInput');
    const resultContainer = document.getElementById('resultContainer');

    // UI Elements
    const contentState = document.getElementById('contentState');
    const loadingState = document.getElementById('loadingState');
    const errorState = document.getElementById('errorState');
    const errorMessage = document.getElementById('errorMessage');

    // Data Fields
    const bookTitle = document.getElementById('bookTitle');
    const bookAuthor = document.getElementById('bookAuthor');
    const bookDescription = document.getElementById('bookDescription');
    const bookLink = document.getElementById('bookLink');

    const API_URL = "https://booksdescription-626114529304.europe-central2.run.app/book";

    // Event Listeners
    searchBtn.addEventListener('click', handleSearch);
    bookInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });

    async function handleSearch() {
        const query = bookInput.value.trim();
        if (!query) return;

        // Reset UI
        showLoading();

        try {
            const url = new URL(API_URL);
            url.searchParams.append('title', query);

            const response = await fetch(url);

            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error(`Can't find a book titled "${query}". Try another one.`);
                }
                throw new Error('Something went wrong. Please try again later.');
            }

            const data = await response.json();
            displayResult(data);
        } catch (error) {
            showError(error.message);
        }
    }

    function showLoading() {
        resultContainer.classList.remove('hidden');
        contentState.classList.add('hidden');
        errorState.classList.add('hidden');
        loadingState.classList.remove('hidden');
    }

    function displayResult(data) {
        loadingState.classList.add('hidden');
        errorState.classList.add('hidden');

        bookTitle.textContent = data.title;
        bookAuthor.textContent = data.author;
        bookDescription.textContent = data.description;
        bookLink.href = data.url;

        contentState.classList.remove('hidden');
    }

    function showError(message) {
        loadingState.classList.add('hidden');
        contentState.classList.add('hidden');
        errorState.classList.remove('hidden');
        errorMessage.textContent = message;
    }
});
