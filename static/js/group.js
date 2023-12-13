const copyToClipboard = async () => {
  try {
    const element = document.querySelector(".invite-code");
    await navigator.clipboard.writeText(element.textContent);
    alert("Copied invite code to clipboard!");
  } catch (error) {
    console.error("Failed to copy to clipboard:", error);
  }
};
