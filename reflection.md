# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

- PetPlanScheduler: works to take the data from the other classes and produce a schedule for the owners to follow.
- PetCareStats: works by organizing the data and logging pet needs like walks, food, medicine, etc.
    Should be able to: know when the pet was fed, when the pet was last walked, if the pet is on any diet or medicine.
- OwnerStats: works by asking the owner questions to record what thier prefrences are for pet care and availibility

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

--- The AI did not originially organize time with duration so we added the ability to keep track of minute

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

--- It prioritises efficiency over redundancy. It was not necessary for the code to have multiple loops for the same general check.

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

- I used the AI to implement the logic and code for the functions desired by the assignment as well as helping me notice flaws I wasn't fully sure would be issues.
- I think prompts with good detail and context that help guide the AI's process to be like how you code help you work with it to find out what its doing.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

--- When the AI formatted the test output it was originally a bit messy so I had it restucture it.

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
    - Edge cases and primary functions
- Why were these tests important?
    - People wont always use the app as intended and will get upset when things that are suppoused to work don't.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

--- I'm moderately comfortable with the results of this project and think if I had more time I'd do more with if people had multiple pets and overlapping tasks.

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
- I think I'm happiest with how it doesn't break and throws exceptions well to users.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
- There were some annoyances I had with the UI and scheduling priorities I'd like to fix.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
- It takes a lot to put all of the moving pieces together and that it can be a struggle to communicate what you want in a way the ai can understand and do
