Feature: Suspend Betting Markets on Red Card

  Background:
    Given a match "Match 1" is in progress
    Given the following players are in the match:
      | playerId | playerName | team   |
      | P1       | Player One | Team A |
      | P2       | Player Two | Team B |
    Given the following betting markets are open for the match:
      | marketId | marketType               | eligiblePlayerIds   |
      | M1       | Player to score          | P1                  |
      | M2       | Anytime Assist Provider   | P2,P1               |
      | M3       | Total Cards              |                     |
      | M4       | First Half Winner        |                     |

  @P0
  Scenario: Immediate suspension of markets upon red card
    When player "Player One" receives a red card
    Then market "M1" should be "Suspended"
    Then market "M2" should be "Suspended"
    Then market "M3" should be "Suspended"
    Then market "M4" should be "Suspended"
    Then no error should have been raised

  @P0
  Scenario: Suspension of markets for player receiving second yellow card
    When player "Player One" receives a second yellow card resulting in a red card
    Then market "M1" should be "Suspended"
    Then market "M2" should be "Suspended"
    Then market "M3" should be "Suspended"
    Then market "M4" should be "Suspended"
    Then no error should have been raised

  @P1
  Scenario: Correct suspension of markets where player is sole subject
    When player "Player One" receives a red card
    Then market "M1" should be "Suspended"
    Then no error should have been raised

  @P1
  Scenario: Correct suspension of markets where player is one of several subjects
    When player "Player Two" receives a red card
    Then market "M2" should be "Suspended"
    Then no error should have been raised

  @P2
  Scenario: Market remains suspended for duration post red card
    When player "Player One" receives a red card
    Then market "M1" should be suspended within 1000ms
    Then market "M2" should be suspended within 1000ms

  @P0
  Scenario: Handling of red card input during no active bets
    When player "Player One" receives a red card
    Then market "M3" should be "Suspended"
    Then no error should have been raised

  @P1
  Scenario: Market suspension timing for near-real-time events
    When player "Player One" receives a red card
    Then market "M1" should be suspended within 500ms
    Then market "M2" should be suspended within 500ms