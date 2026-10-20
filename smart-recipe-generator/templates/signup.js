// signup.js
import supabase from './supabaseClient';

async function signUpUser(name, email, password) {
  // Sign up the user with email and password
  const { user, error } = await supabase.auth.signUp({
    email: email,
    password: password,
    options: {
      data: {
        name: name,  // Store additional user info, like name
      },
    },
  });

  if (error) {
    console.error('Error signing up:', error.message);
    alert(`Signup Error: ${error.message}`);
  } else {
    console.log('User signed up:', user);
    alert('Signup successful! Please provide your profile details.');
    
    // Redirect to profile page to collect user details
    window.location.href = '/profile.html';  
  }
}

// Event listener for form submission
const form = document.getElementById('signup-form');
form.addEventListener('submit', async (event) => {
  event.preventDefault();  // Prevent default form submission

  const name = document.getElementById('name').value;
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  // Call the signUpUser function
  await signUpUser(name, email, password);
});
