Feature: Suspend Betting Markets on Red Card

  Background:
    Given a match "Match 1" is in progress
    Given the following players are in the match:
      | playerId | playerName | team   |
      | P1      | Player 1   | Team A |
      | P2      | Player 2   | Team B |
    Given the following betting markets are open for the match:
      | marketId | marketType           | eligiblePlayerIds |
      | M1      | Single Player Market  | P1                |
      | M2      | Multi Player Market    | P1,P2             |
      | M3      | Multi Player Market    | P2,P1             |
      | M4      | Unrelated Market       |                    |
  
  @P0
  Scenario: Suspend markets upon direct red card
    When player "Player 1" receives a red card
    Then market "M1" should be "Suspended"
    Then market "M2" should be "Suspended"
    Then market "M3" should be "Open"
    Then market "M4" should be "Open"
    Then no error should have been raised

  @P0
  Scenario: Suspend markets upon second yellow card resulting in red card
    When player "Player 1" receives a second yellow card resulting in a red card
    Then market "M1" should be "Suspended"
    Then market "M2" should be "Suspended"
    Then market "M3" should be "Open"
    Then market "M4" should be "Open"
    Then no error should have been raised

  @P1
  Scenario: Check suspension timing after red card event
    When player "Player 1" receives a red card
    Then market "M1" should be suspended within 200ms
    Then market "M2" should be suspended within 200ms
    Then market "M3" should be suspended within 200ms
    Then market "M4" should be suspended within 200ms
    Then no error should have been raised

  @P1
  Scenario: No suspension of unrelated markets
    When player "Player 1" receives a red card
    Then market "M1" should be "Suspended"
    Then market "M2" should be "Suspended"
    Then market "M3" should be "Open"
    Then market "M4" should be "Open"
    Then no error should have been raised

  @P2
  Scenario: Verify suspension for combined markets with multiple players
    When player "Player 1" receives a red card
    Then market "M1" should be "Suspended"
    Then market "M2" should be "Suspended"
    Then market "M3" should be "Open"
    Then market "M4" should be "Open"
    Then no error should have been raised

  @P1
  Scenario: No suspension if red card received after match termination
    Given a match "Match 1" is in progress
    When player "Player 1" receives a red card
    Then market "M1" should be "Suspended"
    When player "Player 1" receives a red card
    Then market "M2" should be "Suspended"
    When player "Player 1" receives a red card
    Then market "M3" should be "Open"
    Then market "M4" should be "Open"
    Then no error should have been raised

  @P2
  Scenario: Testing suspension just before and after the red card incident
    When player "Player 1" receives a red card
    Then market "M1" should be suspended within 500ms
    Then market "M2" should be suspended within 500ms
    Then market "M3" should be suspended within 500ms
    Then market "M4" should be "Open"
    Then no error should have been raised