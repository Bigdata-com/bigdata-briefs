document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('add-form');
    const addButton = document.getElementById('add-button');
    const input = document.getElementById('new-sentence-input');
    const listContainer = document.getElementById('sentence-list');

    // --- FUNCTIONS ---

    // Function to render the list of topic_sentences
    const renderSentences = () => {
        // Clear the current list to avoid duplicates
        listContainer.innerHTML = '';

        // If there are no topic_sentences, display a message
        if (topic_sentences.length === 0) {
            listContainer.innerHTML = `<p class="text-gray-500 text-center p-4">No keyword lines added yet.</p>`;
            return;
        }

        // Create and append an element for each sentence in reverse order
        [...topic_sentences].reverse().forEach((sentence, reverseIndex) => {
            // Calculate the original index for deletion
            const originalIndex = topic_sentences.length - 1 - reverseIndex;
            
            // Create the main container for the list item
            const listItem = document.createElement('div');
            listItem.className = 'flex justify-between items-center bg-white p-4 border border-gray-200 rounded-md shadow-sm text-xs';

            // Create the text element
            const sentenceText = document.createElement('span');
            sentenceText.textContent = sentence;
            sentenceText.className = 'text-gray-700';

            // Create the delete button
            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';
            deleteButton.className = 'bg-red-500 text-white font-semibold px-4 py-1 rounded-md hover:bg-red-600 transition-colors';

            // Add an event listener to the delete button
            deleteButton.addEventListener('click', () => {
                deleteSentence(originalIndex);
            });

            // Append text and button to the list item
            listItem.appendChild(sentenceText);
            listItem.appendChild(deleteButton);

            // Append the list item to the main container
            listContainer.appendChild(listItem);
        });
    };

    // Function to add a new sentence
    const addSentence = () => {
        const newSentence = input.value.trim(); // Get value and remove whitespace
        if (newSentence) { // Only add if the input is not empty
            topic_sentences.push(newSentence);
            input.value = ''; // Clear the input field
            renderSentences(); // Re-render the list
        }
    };

    // Function to delete a sentence by its index
    const deleteSentence = (indexToDelete) => {
        // Filter out the sentence at the specified index
        topic_sentences = topic_sentences.filter((_, index) => index !== indexToDelete);
        renderSentences(); // Re-render the list
    };

    // --- EVENT LISTENERS ---

    // Listen for form submission (e.g., pressing Enter)
    form.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent page reload
        addSentence();
    });

    // Listen for clicks on the add button
    addButton.addEventListener('click', (event) => {
        event.preventDefault(); // Prevent form submission
        addSentence();
    });

    // --- INITIAL RENDER ---
    // Render the initial list when the page loads
    renderSentences();
});