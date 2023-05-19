import logo from './assets/logo.png';
import { useState } from 'react';
import axios from 'axios';

function App() {
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [answer, setAnswer] = useState('');

  const apiUrl = import.meta.env.VITE_BACKEND_URL;

  const handleButtonClick = async () => {
    if (inputValue.trim() === '') {
      console.log('Input field is empty');
      alert('Input field is empty');
      return;
    }

    setIsLoading(true); // Start loading

    try {
      const response = await axios.post(`${apiUrl}/ask`, { question: inputValue });
      const answer = response.data.answer;

      console.log('API response:', response.data);
      console.log('Answer:', answer);

      setAnswer(answer); // Set the answer
      setInputValue(''); // Reset the input value to empty
    } catch (error) {
      console.error('API request error:', error);
      alert('An error occurred while fetching the answer. Please try again.');
    } finally {
      setIsLoading(false); // Stop loading
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleButtonClick();
    }
  };

  return (
    <>
      <div className="flex justify-center items-center">
        <img src={logo} alt="" width="300" height="300" className="mt-16" />
      </div>
      <div className="flex flex-col justify-center items-center mt-12">
        <div className="form-control w-full max-w-4xl">
          <label className="label">
            <span className="label-text">
              Write your queries to get helped by mydukaanGPT.
            </span>
          </label>
          <input
            type="text"
            placeholder="Type here"
            className="input input-bordered w-full max-w-4xl"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <div>
            <button className="btn mt-2 btn-primary" onClick={handleButtonClick}>
              {isLoading ? 'Loading...' : 'Get Answer'}
            </button>
          </div>
        </div>
        <div className="artboard artboard-horizontal phone-5 mt-8">
          {answer}
        </div>
      </div>
    </>
  );
}

export default App;