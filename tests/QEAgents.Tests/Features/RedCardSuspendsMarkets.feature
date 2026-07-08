Feature: Suspend Betting Markets on Red Card

  Background:
    Given a match "Match 1" is in progress
    Given the following players are in the match: 
      | playerId | playerName | team   |
      | P1      | Player 1   | Team A |
      | P2      | Player 2   | Team B |
    Given the following betting markets are open for the match: 
      | marketId | marketType                | eligiblePlayerIds  |
      | M1      | Player to score anytime    | P1                 |
      | M2      | Next Card                  | P1,P2              |
      | M3      | Total Goals                 |                     |
      | M4      | Player to receive yellow card| P2                 |

  @P0
  Scenario: Suspend betting markets immediately on red card receipt
    When player "Player 1" receives a red card
    Then market "M1" should be "Suspended"
    Then market "M2" should be "Suspended"
    Then market "M3" should be "Open"
    Then market "M4" should be "Open"
    Then no error should have been raised

  @P0
  Scenario: Suspend markets with player as sole subject on red card receipt
    When player "Player 1" receives a red card
    Then market "M1" should be "Suspended"
    Then no error should have been raised

  @P1
  Scenario: Suspend markets with player among multiple options on red card receipt
    When player "Player 1" receives a red card
    Then market "M2" should be "Suspended"
    Then no error should have been raised

  @P1
  Scenario: Handle second yellow card as a red card
    When player "Player 2" receives a second yellow card resulting in a red card
    Then market "M2" should be "Suspended"
    Then no error should have been raised

  @P0
  Scenario: Test suspension delay (boundary case)
    When player "Player 1" receives a red card
    Then market "M1" should be suspended within 1000ms
    Then market "M2" should be suspended within 1000ms
    Then no error should have been raised

  @P2
  Scenario: Verify non-suspension of unrelated markets
    When player "Player 1" receives a red card
    Then market "M3" should be "Open"
    Then market "M4" should be "Open"
    Then no error should have been raised