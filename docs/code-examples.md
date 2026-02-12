An example of a codeblock for Python:

### Code Blocks

=== "Python Code"

    ```py title='add_numbers.py' linenums='1' hl_lines='6'

    # Function to add two numbers
    def add_two_numbers(num1, num2):
        return num1 + num2

    # Example usage
    result = add_two_numbers(5, 3)
    print('The sum is:', result)
    ```

=== "The code again"

    ```py title='add_numbers.py' linenums='1' hl_lines='7'
    # Function to add two numbers
    def add_two_numbers(num1, num2):
        return num1 + num2

    # Example usage
    result = add_two_numbers(5, 3)
    print('The sum is:', result)
    ```

!!! note "This is amazing"

    Where are we?

??? note "This is hidden"

    Where are we?

## Flowchart

```mermaid
graph LR
  A[Start] --> B{Failure?};
  B -->|Yes| C[Investigate...];
  C --> D[Debug];
  D --> B;
  B ---->|No| E[Success!];
```

## Sequence Diagrams

```mermaid
sequenceDiagram
  autonumber
  Server->>Terminal: Send request
  loop Health
      Terminal->>Terminal: Check for health
  end
  Note right of Terminal: System online
  Terminal-->>Server: Everything is OK
  Terminal->>Database: Request customer data
  Database-->>Terminal: Customer data
```

``` mermaid
classDiagram
  Person <|-- Student
  Person <|-- Professor
  Person : +String name
  Person : +String phoneNumber
  Person : +String emailAddress
  Person: +purchaseParkingPass()
  Address "1" <-- "0..1" Person:lives at
  class Student{
    +int studentNumber
    +int averageMark
    +isEligibleToEnrol()
    +getSeminarsTaken()
  }
  class Professor{
    +int salary
  }
  class Address{
    +String street
    +String city
    +String state
    +int postalCode
    +String country
    -validate()
    +outputAsLabel()
  }
```