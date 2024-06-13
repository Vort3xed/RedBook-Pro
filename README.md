# RedBook-Pro

Sample questions pulled from: problemset14.pdf

Test codecs:
- Reading/Writing: RD
- Math: MH

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