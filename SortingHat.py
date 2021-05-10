#!/usr/bin/env python3

import argparse
import collections
import pandas
import os
import sys

def main(arguments):
    # Parse Arguments
    parser = argparse.ArgumentParser(description='Sort freshmen by house.')
    parser.add_argument('file_input', metavar='filename.csv', nargs='?',
                        help='csv file as input')
    parser.add_argument('file_output', metavar='filename2.csv', nargs='?',
                        help='csv file for output')
    parser.add_argument('house_names', metavar='houses.txt', nargs='?',
                        help='line by line input for house names')
    parser.add_argument('-g', metavar=('min', 'max'), type=float, nargs=2,
                        default=[0.45,0.55],
                        help='acceptable gender coefficient from 0 to 1, default [0.45,0.55]')
    parser.add_argument('-s', metavar=('distribution', 'niche'), type=float, nargs=2,
                        default=[0.2,0.8],
                        help='acceptable school coefficient for distributing students ' +
                        'from the same school and congregating students from niche schools' +
                        ' from 0 to 1, default [0.2,0.8]')
    parser.add_argument('-m', metavar=('distribution', 'niche'), type=float, nargs=2,
                        default=[0.2,1],
                        help='acceptable major coefficient for distributing students ' +
                        'from the same major and congregating students from niche major' +
                        ' from 0 to 1, default [0.2,1]')
    args = parser.parse_args(arguments)
    print("Input file: ",args.file_input)
    print("Output file: ",args.file_output)

    # House List
    houses = []
    with open(args.house_names) as f:
        for line in f:
            houses.append(line.strip())
    f.close()
    assert len(houses) >= 4
    print("Your houses are: ", ", ".join(houses))

    # Read CSV
    df = pandas.read_csv(args.file_input)
    df['Hash'] = [hash(i) for i in df['Name']]
    df = df.sort_values(by='Hash')

    schools = collections.Counter(df['School'])
    maximum = max(schools, key=schools.get)
    school_coeffs = {key:(schools[key]-2)/(schools[maximum]-2)*(args.s[1]-args.s[0])+args.s[0] for key in schools}

    majors = collections.Counter(df['Major'])
    maximum = max(majors, key=majors.get)
    major_coeffs = {key:(majors[key]-2)/(majors[maximum]-2)*(args.m[1]-args.m[0])+args.m[0] for key in majors}

    # Populate adjacency list

    n = len(df['Hash'])
    m = len(houses)

    adjList = []
    for i in df.itertuples():
        row = {}
        for j in df.itertuples():
            magnitude = (mag(school_coeffs[i[3]]) if i[3] == j[3] else 0) + (mag(major_coeffs[i[5]]) if i[5] == j[5] else 0)
            direction = (dir(school_coeffs[i[3]]) if i[3] == j[3] else 0) + (dir(major_coeffs[i[5]]) if i[5] == j[5] else 0)
            row[j[6]] = 0.5 + magnitude*direction*(2*n)
        adjList.append(row)

    # Colouring Algorithm 1

    hashes = [x for x in df['Hash']]
    colours = [-1] * n

    colours[0] = 0
    for i in range(1,n):
        count = {j:colours.count(j) for j in range(0,6)}
        count_sorted = [x[0] for x in sorted(count.items(), key=lambda count: count[1]+count[0]/m)]
        temp = [0] * m
        for index, j in enumerate(count_sorted):
            temp[j] += (m - index - 1)
        for j in range(0,i):
            temp[colours[j]] += adjList[i][hashes[j]]
        for x in temp:
            if x in count and count[x]!=0:
                x = x/count[x]
        colours[i] = sorted(enumerate(temp), key=lambda x: x[1], reverse=True)[0][0]

    df['Houses'] = [houses[x] for x in colours]
    df = df.sort_index()

    # Output
    df = df.drop(columns=['Hash'])
    df.to_csv(args.file_output)

def dir(x):
    return min(x,1-x)

def mag(x):
    return max(x-0.5,0.5-x)
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))