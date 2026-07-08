Feature: Red card suspends related betting markets
  As a risk & trading operator
  I want all open betting markets related to a player to be suspended the moment that player is sent off
  So that the platform cannot take further bets on markets whose outcome the dismissal has just affected

  Background:
    Given a match "Riverside FC vs Oakdale United" is in progress
    And the following players are in the match:
      | playerId | playerName  | team           |
      | P1       | Marco Silva | Riverside FC   |
      | P2       | Tomas Reyes | Oakdale United |
    And the following betting markets are open for the match:
      | marketId | marketType               | eligiblePlayerIds |
      | M1       | Player to Score Anytime  | P1                |
      | M2       | Anytime Assist Provider  | P2,P1             |
      | M3       | Match Winner             |                   |
      | M4       | Next Card                | P2,P1             |

  @P0
  Scenario: Direct red card suspends the player's primary market
    When player "Marco Silva" receives a red card
    Then market "M1" should be "Suspended"

  @P0
  Scenario: Red card suspends markets where the player is a secondary eligible selection
    When player "Marco Silva" receives a red card
    Then market "M2" should be "Suspended"
    And market "M4" should be "Suspended"

  @P1
  Scenario: Markets unrelated to the sent-off player remain open
    When player "Marco Silva" receives a red card
    Then market "M3" should be "Open"

  @P1
  Scenario: Second yellow card converting to red also suspends related markets
    When player "Tomas Reyes" receives a second yellow card resulting in a red card
    Then market "M2" should be "Suspended"
    And market "M4" should be "Suspended"

  @P2
  Scenario: Duplicate red card event for the same player is idempotent
    When player "Marco Silva" receives a red card
    And player "Marco Silva" receives a red card again
    Then market "M1" should be "Suspended"
    And no error should have been raised

  @P0
  Scenario: Suspension keeps pace with the near-real-time SLA
    When player "Marco Silva" receives a red card
    Then market "M1" should be suspended within 100ms
