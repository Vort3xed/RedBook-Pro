# RedBook-Pro

Sample questions pulled from: problemset14.pdf

Codec lookup table:
- Reading/Writing: RD
  - Central Ideas and Details: CID
  - Command of Evidence: CE
  - Words in Context: WC
  - Text Structure and Purpose: TSP
  - Cross-Text Connections: CTC
  - Rhetorical Synthesis: RS
  - Transitions: T
  - Boundaries: B
  - Form, Structure, and Sense: FSS
---
- Math: MH
  - in progress :D
### Firestore structure:
```
.
├── accounts/
│   ├── sample_user/
│   │   ├── answered: []
│   │   ├── answered_correctly: []
│   │   └── answered_incorrectly: []
│   └── ...
├── reading_questions/
│   ├── sample_question/
│   │   ├── correctAnswer: string
│   │   ├── difficulty: string
│   │   ├── phototype: string
│   │   └── skill: string
│   └── ...
└── math_questions/
    ├── sample_question/
    │   ├── correctAnswer: string
    │   ├── difficulty: string
    │   ├── phototype: string
    │   └── skill: string
    └── ...
```

### Firebase Storage structure:
```
.
├── image_1.png
├── image_2.png
├── image_3.png
└── ...
```

TODO:
- ~~collect selected answer~~
- ~~determine if question was answered correctly~~
- ~~redirect to dashboard once questions are all answered~~
- ~~map quiz params to the actual query~~
- add math questions
- show statistics
- css and styling
- add more questions
- DATA SANITIZATION (dont break database)