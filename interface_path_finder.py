from tkinter import *

global passing_var
passing_var = 0


def choose(algorithm):
    print('_____________________')
    print('You chose ' + algorithm)
    global passing_var
    passing_var = algorithm


def get_algorithm():
    global passing_var
    root = Tk()
    root.title('Finn')

    info_label = Label(root, text='Choose an algorithm', padx=60,
                       pady=20).grid(row=0, columnspan=2)

    quit_but = Button(root, text='start', padx=60, pady=20,
                      command=root.destroy).grid(row=4, columnspan=2)

    a_star = Button(root, text='A*', padx=40, pady=20,
                    command=lambda: choose('A_star')).grid(row=1, column=0)

    # for other algorithms
    dijkstra = Button(root, text='Dijkstra', padx=27, pady=20,
                      command=lambda: choose('Dijkstra')).grid(row=1, column=1)
    gbfs = Button(root, text='gbfs', padx=40, pady=20,
                  command=lambda: choose('Greedy_best_first_search')).grid(row=2, column=0)
    some_button2 = Button(root, text='fill', padx=40, pady=20,
                          command=lambda: choose('fill')).grid(row=2, column=1)

    root.mainloop()

    return passing_var


if __name__ == '__main__':
    print(get_algorithm())
