from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random
from django import forms

author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'ns_experiment_single'
    players_per_group = 2   #***
    rounds_per_partner = 41
    num_rounds = rounds_per_partner*4 + 1  #***
    num_items = 7  # ***

    pizza_types = ["Hawaiian", "Pepperoni", "Sausage & Mushroom", "Tomato & Basil", "BBQ Chicken", "Meat Lover's", "Vegan"]   #***
    movie_types = ["Horror", "Comedy", "Action", "Musical", "Documentary", "Sci-Fi", "Drama"]   #***


class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1 or self.round_number % Constants.rounds_per_partner == 0:
            self.group_randomly()

            if self.round_number == 1:
                for g in self.get_groups():
                    item_type = random.choice(["pizzas", "movies"])  # ***

                    if item_type == "pizzas":
                        outcomes = Constants.pizza_types # ***

                    else:
                        outcomes = Constants.movie_types  # ***

                    outcome_pairs = [[x, y] for x in outcomes for y in outcomes if outcomes.index(x) < outcomes.index(y)]

                    for p in g.get_players():
                        p.participant.vars['num_items'] = Constants.num_items
                        p.participant.vars['item_type'] = item_type
                        p.participant.vars['outcomes'] = outcomes
                        p.participant.vars['outcome_pairs'] = outcome_pairs

                for player in self.get_players():
                    #Initialize a bunch of participant.vars variables
                    player.participant.vars['movie_utils'] = [0]*(len(Constants.movie_types))
                    player.participant.vars['pizza_utils'] = [0]*(len(Constants.pizza_types))
                    player.participant.vars['self_utils'] = [0]*(player.participant.vars['num_items'])    #***

                    player.participant.vars['likert_info_p'] = list()  #(outcome, likert_answer) #***
                    player.participant.vars['likert_info_m'] = list()  #(outcome, likert_answer) #***
                    player.participant.vars['scale_max_value'] = 0.5
                    player.participant.vars['options_to_display'] = ('x', 'y')  #***
                    player.participant.vars['success_pairs'] = []   #***
                    player.participant.vars['disagree_count'] = 0   #***
                    player.participant.vars['modif_count'] = 0   #***
                    player.participant.vars['end_experiment'] = False   #***
                    player.participant.vars['reach_equilibrium'] = False    #***
                    player.participant.vars['payoff_history'] = dict()

        else:
            if self.round_number in range(1, Constants.rounds_per_partner):
                last_round_grouped = 1
            elif self.round_number in range(Constants.rounds_per_partner+1, Constants.rounds_per_partner*2):
                last_round_grouped = Constants.rounds_per_partner
            elif self.round_number in range(Constants.rounds_per_partner*2+1, Constants.rounds_per_partner*3):
                last_round_grouped = Constants.rounds_per_partner*2
            elif self.round_number in range(Constants.rounds_per_partner*3+1, Constants.rounds_per_partner*4):
                last_round_grouped = Constants.rounds_per_partner*3
            else:
                last_round_grouped = Constants.rounds_per_partner*4

            self.group_like_round(last_round_grouped)


class Group(BaseGroup):
    def set_payoffs(self):
        if self.subsession.round_number % Constants.rounds_per_partner < 2:
            for p in self.get_players():
                #No payoff for instruction pages and Individual Task
                p.payoff = c(0)
        else:
            if self.get_player_by_id(1).round_result == "Agree":
                for p in self.get_players():
                    best_choice = p.best_choice
                    if p.participant.vars['item_type'] == "movies":
                        index = Constants.movie_types.index(best_choice)
                        p.payoff = p.participant.vars['movie_payoffs'][index]
                    else:
                        index = Constants.pizza_types.index(best_choice)
                        p.payoff = p.participant.vars['pizza_payoffs'][index]

            else:
                for p in self.get_players():
                    p.payoff = c(0)


class Player(BasePlayer):
    gender = models.StringField(choices=['Male', 'Female', 'Other'],
                                verbose_name='Which gender do you currently identify with the most?',
                                widget=widgets.RadioSelect,
                                blank=True)
    major = models.StringField(verbose_name='What is your major at UCI?',
                               blank=True)


    quiz1 = models.StringField(choices=random.sample(['Black', 'Red'], 2),
                               verbose_name="1. The labels of which color represent your beliefs about you partner's liking of an item?",
                               widget=widgets.RadioSelect)
    def quiz1_error_message(self,value):
        if value != 'Red':
            return 'The answer to question 1 is wrong, please try again.'

    quiz2 = models.StringField(choices=random.sample(['Yes', 'No'], 2),
                               verbose_name='2. Can you move the black labels?',
                               widget=widgets.RadioSelect)
    def quiz2_error_message(self,value):
        if value != 'No':
            return 'The answer to question 2 is wrong, please try again.'

    quiz3 = models.StringField(choices=random.sample(['$0.00', '$1.00', '$0.05'], 3),
                               verbose_name='3. How much does it cost per round to move the red labels?',
                               widget=widgets.RadioSelect)
    def quiz3_error_message(self,value):
        if value != '$0.05':
            return 'The answer to question 3 is wrong, please try again.'

    quiz4 = models.StringField(choices=random.sample(['4; 1', '5; 1', '4; 2', '5; 2'], 4),
                               verbose_name='4. Out of _____ total interactions, _____ of them will just be for practice.',
                               widget=widgets.RadioSelect)

    def quiz4_error_message(self, value):
        if value != '4; 1':
            return 'The answer to question 4 is wrong, please try again.'

    quiz5 = models.StringField(choices=random.sample(['5', '10', '1'], 3),
                                verbose_name='5. An interaction must have at least ______ rounds to be eligible for payment',
                                widget=widgets.RadioSelect)
    def quiz5_error_message(self,value):
        if value != '5':
            return 'The answer to question 5 is wrong, please try again.'

    quiz6 = models.StringField(choices=random.sample(['for 5 consecutive rounds', 'for 10 consecutive rounds'], 2),
                               verbose_name='6. An interaction will end if you and your partner have agreements',
                               widget=widgets.RadioSelect)
    def quiz6_error_message(self,value):
        if value != 'for 10 consecutive rounds':
            return 'The answer to question 6 is wrong, please try again.'

    quiz7 = models.StringField(choices=random.sample(['$0.00', '$0.05'], 2),
                               verbose_name='7. If a rounds is chosen for payment and you and your partner had a disagreement'
                                            ' in it, the round will earn you',
                               widget=widgets.RadioSelect)
    def quiz7_error_message(self,value):
        if value != '$0.00':
            return 'The answer to question 7 is wrong, please try again.'

    quiz8 = models.StringField(choices=random.sample(['The option you personally prefer', 'The option implied by your models to be best for you and your partner'], 2),
                               verbose_name='8. In the game, what is meant by "your choice"?',
                               widget=widgets.RadioSelect)

    def quiz8_error_message(self,value):
        if value != 'The option implied by your models to be best for you and your partner':
            return 'The answer to question 8 is wrong, please try again.'


    strategy = models.StringField(choices=['Yes', 'No'],
                                verbose_name="Did you follow any strategy for updating your model of your partner's preferences?",
                                widget=widgets.RadioSelect,
                                blank=True)
    strategy_changed = models.StringField(choices=['Yes', 'No', 'N/A'],
                                verbose_name='Did your strategy change with time?',
                                widget=widgets.RadioSelect,
                                blank=True)
    strategy_changed_why = models.LongStringField(verbose_name='If yes, why?',
                                                  widget=forms.Textarea(attrs={'rows':'3', 'cols': '7'}), blank=True)
    strategy_comments = models.LongStringField(verbose_name='Would you please describe the strategies you followed (if any)?',
                                               widget=forms.Textarea(attrs={'rows':'5', 'cols': '7'}), blank=True)

    m_liking_in_words1 = models.StringField(choices=random.sample(["love", "sometimes enjoy", "hate",
                                                             "am not fond of", "get excited about",
                                                              "am displeased by", "don't care for"], 7))
    m_liking_in_words2 = models.StringField(choices=random.sample(["love", "sometimes enjoy", "hate",
                                                             "am not fond of", "get excited about",
                                                              "am displeased by", "don't care for"], 7))
    m_liking_in_words3 = models.StringField(choices=random.sample(["love", "sometimes enjoy", "hate",
                                                             "am not fond of", "get excited about",
                                                              "am displeased by", "don't care for"], 7))
    m_liking_in_words4 = models.StringField(choices=random.sample(["love", "sometimes enjoy", "hate",
                                                             "am not fond of", "get excited about",
                                                              "am displeased by","don't care for"], 7))
    m_liking_in_words5 = models.StringField(choices=random.sample(["love", "sometimes enjoy", "hate",
                                                             "am not fond of", "get excited about",
                                                              "am displeased by","don't care for"], 7))
    m_liking_in_words6 = models.StringField(choices=random.sample(["love", "sometimes enjoy", "hate",
                                                             "am not fond of", "get excited about",
                                                              "am displeased by","don't care for"], 7))
    m_liking_in_words7 = models.StringField(choices=random.sample(["love", "sometimes enjoy", "hate",
                                                             "am not fond of", "get excited about",
                                                              "am displeased by", "don't care for"], 7))
    p_liking_in_words1 = models.StringField(choices=random.sample(["love", "sometimes enjoy", "hate",
                                                                   "am not fond of", "get excited about",
                                                                   "am displeased by", "don't care for"], 7))
    p_liking_in_words2 = models.StringField(choices=random.sample(["love", "sometimes enjoy", "hate",
                                                                   "am not fond of", "get excited about",
                                                                   "am displeased by", "don't care for"], 7))
    p_liking_in_words3 = models.StringField(choices=random.sample(["love", "sometimes enjoy", "hate",
                                                                   "am not fond of", "get excited about",
                                                                   "am displeased by", "don't care for"], 7))
    p_liking_in_words4 = models.StringField(choices=random.sample(["love", "sometimes enjoy", "hate",
                                                                   "am not fond of", "get excited about",
                                                                   "am displeased by", "don't care for"], 7))
    p_liking_in_words5 = models.StringField(choices=random.sample(["love", "sometimes enjoy", "hate",
                                                                   "am not fond of", "get excited about",
                                                                   "am displeased by", "don't care for"], 7))
    p_liking_in_words6 = models.StringField(choices=random.sample(["love", "sometimes enjoy", "hate",
                                                                   "am not fond of", "get excited about",
                                                                   "am displeased by", "don't care for"], 7))
    p_liking_in_words7 = models.StringField(choices=random.sample(["love", "sometimes enjoy", "hate",
                                                                   "am not fond of", "get excited about",
                                                                   "am displeased by", "don't care for"], 7))

    m_outcome1 = models.FloatField()
    m_outcome2 = models.FloatField()
    m_outcome3 = models.FloatField()
    m_outcome4 = models.FloatField()
    m_outcome5 = models.FloatField()
    m_outcome6 = models.FloatField()
    m_outcome7 = models.FloatField()

    p_outcome1 = models.FloatField()
    p_outcome2 = models.FloatField()
    p_outcome3 = models.FloatField()
    p_outcome4 = models.FloatField()
    p_outcome5 = models.FloatField()
    p_outcome6 = models.FloatField()
    p_outcome7 = models.FloatField()

    opp_util_model_1 = models.FloatField(initial=0)
    opp_util_model_2 = models.FloatField(initial=0)
    opp_util_model_3 = models.FloatField(initial=0)
    opp_util_model_4 = models.FloatField(initial=0)
    opp_util_model_5 = models.FloatField(initial=0)
    opp_util_model_6 = models.FloatField(initial=0)
    opp_util_model_7 = models.FloatField(initial=0)

    tradeoff_constant = models.FloatField() #***

    best_choice = models.StringField(initial="")    #***
    round_result = models.StringField(initial="")   #***

    participant_vars_dump = models.StringField()

    Q01 = models.IntegerField(blank=True)
    Q02 = models.IntegerField(blank=True)
    Q03 = models.IntegerField(blank=True)
    Q04 = models.IntegerField(blank=True)
    Q05 = models.IntegerField(blank=True)
    Q06 = models.IntegerField(blank=True)
    Q07 = models.IntegerField(blank=True)
    Q08 = models.IntegerField(blank=True)
    Q09 = models.IntegerField(blank=True)
    Q10 = models.IntegerField(blank=True)
    Q11 = models.IntegerField(blank=True)
    Q12 = models.IntegerField(blank=True)
    Q13 = models.IntegerField(blank=True)
    Q14 = models.IntegerField(blank=True)
    Q15 = models.IntegerField(blank=True)
    Q16 = models.IntegerField(blank=True)
    Q17 = models.IntegerField(blank=True)
    Q18 = models.IntegerField(blank=True)
    Q19 = models.IntegerField(blank=True)
    Q20 = models.IntegerField(blank=True)
    Q21 = models.IntegerField(blank=True)
    Q22 = models.IntegerField(blank=True)
    Q23 = models.IntegerField(blank=True)
    Q24 = models.IntegerField(blank=True)
    Q25 = models.IntegerField(blank=True)
    Q26 = models.IntegerField(blank=True)
    Q27 = models.IntegerField(blank=True)
    Q28 = models.IntegerField(blank=True)
    Q29 = models.IntegerField(blank=True)
    Q30 = models.IntegerField(blank=True)
    Q31 = models.IntegerField(blank=True)
    Q32 = models.IntegerField(blank=True)
    Q33 = models.IntegerField(blank=True)
    Q34 = models.IntegerField(blank=True)
    Q35 = models.IntegerField(blank=True)
    Q36 = models.IntegerField(blank=True)
    Q37 = models.IntegerField(blank=True)
    Q38 = models.IntegerField(blank=True)
    Q39 = models.IntegerField(blank=True)
    Q40 = models.IntegerField(blank=True)
    Q41 = models.IntegerField(blank=True)
    Q42 = models.IntegerField(blank=True)
    Q43 = models.IntegerField(blank=True)
    Q44 = models.IntegerField(blank=True)

    def get_partner(self):
        return self.get_others_in_group()[0]


    # def set_opp_model(self, likert_values):
    #     outcome_index = self.participant.vars['outcomes'].index(likert_outcome)
    #
    #     opp_util_model[outcome_index] = likert_value[outcome_index]

    def set_tradeoff_constant(self):
        '''Calculates the trade-off constant for the player based on his/her initial utility models.'''

        numerator = max(self.participant.vars['self_utils']) - min(self.participant.vars['self_utils'])
        opp_util_model = [self.opp_util_model_1, self.opp_util_model_2, self.opp_util_model_3,
                              self.opp_util_model_4, self.opp_util_model_5, self.opp_util_model_6,
                              self.opp_util_model_7]
        denominator = max(opp_util_model) - min(opp_util_model)
        self.tradeoff_constant = numerator/denominator

    def pick_pair(self, seed_value):
        '''Pick a random pair of options that have not yet been agreed upon.'''

        non_success_pairs = [pair for pair in self.participant.vars['outcome_pairs'] if pair not in self.participant.vars['success_pairs']]
        random.seed(seed_value)
        index = random.randint(0, len(non_success_pairs) - 1)
        return non_success_pairs[index]

    def best_option(self, option1, option2):
        '''Returns the option that, according to the player's utility models, yields the highest sum of utilities.'''

        opp_util_model = [self.opp_util_model_1, self.opp_util_model_2, self.opp_util_model_3,
                  self.opp_util_model_4, self.opp_util_model_5, self.opp_util_model_6,
                  self.opp_util_model_7]
        opt1_index = self.participant.vars['outcomes'].index(option1)
        opt2_index = self.participant.vars['outcomes'].index(option2)
        self_vals = (self.participant.vars['self_utils'][opt1_index], self.participant.vars['self_utils'][opt2_index])
        opp_vals = (opp_util_model[opt1_index], opp_util_model[opt2_index])
        joint_opt1 = self_vals[0] + opp_vals[0]
        joint_opt2 = self_vals[1] + opp_vals[1]
        if joint_opt1 > joint_opt2:
            choice = option1
        elif joint_opt1 < joint_opt2:
            choice = option2
        else:
            #Sum of utilities is equal --> pick one randomly
            coin_flip = random.randint(0, 1)
            if coin_flip == 0:
                choice = option1
            else:
                choice = option2
        self.best_choice = choice

    def update_tradeoff_constant(self, p):
        self.tradeoff_constant = p * self.in_round(self.subsession.round_number-1).tradeoff_constant

    def get_prev_opp_model(self):
        self_last_round = self.in_round(self.subsession.round_number-1)

        self.opp_util_model_1 = self_last_round.opp_util_model_1
        self.opp_util_model_2 = self_last_round.opp_util_model_2
        self.opp_util_model_3 = self_last_round.opp_util_model_3
        self.opp_util_model_4 = self_last_round.opp_util_model_4
        self.opp_util_model_5 = self_last_round.opp_util_model_5
        self.opp_util_model_6 = self_last_round.opp_util_model_6
        self.opp_util_model_7 = self_last_round.opp_util_model_7

    def join_lists(self, list1, list2):
        '''For list1 = [l1, l2, l3, ...] and list2 = [m1, m2, m3, ...], returns [(l1, m1), (l2, m2), ...].
        Assumes list1 and list2 are the same length.'''

        joined_list = []
        for i in range(len(list1)):
            joined_list.append((list1[i], list2[i]))

        return joined_list

    def round_to_quarter(self, value):
        two_decimal = round(value, 2)
        (dollars, cents) = str(two_decimal).split(".")
        dollars = int(dollars)
        cents = int(cents)
        if cents > 0 and cents < 25:
            cents = 25
        elif cents > 25 and cents < 50:
            cents = 50
        elif cents > 50 and cents < 75:
            cents = 75
        elif cents > 75:
            cents = 0
            dollars += 1

        return dollars + cents*0.01


