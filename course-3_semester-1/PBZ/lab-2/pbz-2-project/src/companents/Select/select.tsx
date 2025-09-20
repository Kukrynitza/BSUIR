'use client'
import React, { useState, useEffect } from 'react';
import * as Select from '@radix-ui/react-select';
import styles from './select.module.css';

interface Option {
    value: string;
    label: string;
}

interface CustomSelectProps {
    options: Option[];
    defaultValue: string;
    id: number | undefined;
    onValueChange: (id: number | undefined, value: string) => void;
}

const CustomSelect = ({ options, defaultValue, id, onValueChange }: CustomSelectProps) => {
  const [selectedValue, setSelectedValue] = useState(defaultValue);

  useEffect(() => {
    setSelectedValue(defaultValue);
  }, [defaultValue]);

  const handleValueChange = (value: string) => {
    setSelectedValue(value);
    if(id) {
      onValueChange(id, value);
    } else {
      onValueChange(undefined, value);
    }
  };

  return (
    <Select.Root value={selectedValue} onValueChange={handleValueChange}>
      <Select.Trigger className={styles.simple_select_trigger}>
        <Select.Value placeholder="Выберите значение" />
      </Select.Trigger>

<Select.Portal>
  <Select.Content 
    className={styles.simple_select_content}
    position="item-aligned"
    sideOffset={5}
  >
    <Select.Viewport className={styles.simple_select_viewport}>
      {options.map((option, index) => (
        <Select.Item 
          key={`${option.value}-${index}`}
          value={option.value}
          className={styles.simple_select_item}
        >
          <Select.ItemText>{option.label}</Select.ItemText>
        </Select.Item>
      ))}
    </Select.Viewport>
  </Select.Content>
</Select.Portal>
    </Select.Root>
  );
};

export default CustomSelect;